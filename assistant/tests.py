from unittest.mock import patch

from django.contrib.auth.models import User
from django.db import DatabaseError
from django.test import Client, SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from analyses.models import Analysis
from resumes.models import JobDescription, Resume

from .models import ChatMessage
from .services import (
    HISTORY_LIMIT,
    MAX_CV_LENGTH,
    answer_question,
    build_user_prompt,
    format_analysis,
    get_history,
    parse_reply,
    save_exchange,
)

CHUNKS = [
    {"id": "help-05", "title": "File rules", "content": "PDF or DOCX.", "similarity": 0.585},
    {"id": "help-04", "title": "Run analysis", "content": "Press Start.", "similarity": 0.463},
]


def create_analysis(user, result_data=None):
    return Analysis.objects.create(
        user=user,
        resume=Resume.objects.create(user=user, file="resumes/cv.pdf", extracted_text="CV text"),
        job_description=JobDescription.objects.create(
            user=user,
            job_title="Backend Developer",
            content="Needs Docker",
        ),
        supplementary_text="Notes",
        result_data={"gaps": ["Learn Docker"]} if result_data is None else result_data,
    )


class AnswerQuestionTests(SimpleTestCase):
    @patch("assistant.services.retrieve_chunks", return_value=CHUNKS)
    @patch("assistant.services.generate_answer")
    def test_keeps_only_sources_that_were_retrieved(self, generate, _retrieve):
        generate.return_value = {"answer": "Yes.", "source_ids": ["help-05", "help-99"]}

        result = answer_question("Can I upload DOCX?")

        self.assertEqual([chunk["id"] for chunk in result["sources"]], ["help-05"])

    @patch("assistant.services.retrieve_chunks", return_value=CHUNKS)
    @patch("assistant.services.generate_answer")
    def test_no_sources_when_the_materials_do_not_cover_the_question(self, generate, _retrieve):
        generate.return_value = {"answer": "Not covered.", "source_ids": []}

        result = answer_question("Can it write a cover letter?")

        self.assertEqual(result["sources"], [])
        self.assertEqual(len(result["retrieved"]), 2)

    @patch("assistant.services.retrieve_chunks", return_value=CHUNKS)
    @patch("assistant.services.generate_answer", return_value={"answer": "  "})
    def test_empty_answer_is_an_error(self, _generate, _retrieve):
        with self.assertRaises(ValueError):
            answer_question("Hello?")

    def test_prompt_contains_the_question_and_each_chunk(self):
        prompt = build_user_prompt("Can I upload DOCX?", CHUNKS)

        self.assertIn("Can I upload DOCX?", prompt)
        self.assertIn('<material id="help-05">\nPDF or DOCX.\n</material>', prompt)
        self.assertIn('<material id="help-04">', prompt)


class ParseReplyTests(SimpleTestCase):
    def test_splits_the_answer_from_the_sources_line(self):
        self.assertEqual(
            parse_reply("Learn Docker.\nThen AWS.\n\nSOURCES: help-05, analysis\n"),
            {"answer": "Learn Docker.\nThen AWS.", "source_ids": ["help-05"], "used_analysis": True},
        )

    def test_none_means_no_sources(self):
        self.assertEqual(
            parse_reply("Not covered.\nsources: none"),
            {"answer": "Not covered.", "source_ids": [], "used_analysis": False},
        )

    def test_answer_without_a_sources_line_is_kept(self):
        self.assertEqual(
            parse_reply("Just an answer."),
            {"answer": "Just an answer.", "source_ids": [], "used_analysis": False},
        )

    def test_sources_inside_the_answer_are_not_the_final_line(self):
        reply = parse_reply("SOURCES: cite your work.\nGood luck.")

        self.assertEqual(reply["answer"], "SOURCES: cite your work.\nGood luck.")

    def test_only_a_sources_line_gives_an_empty_answer(self):
        self.assertEqual(parse_reply("SOURCES: none")["answer"], "")


class ChatViewTests(TestCase):
    def setUp(self):
        self.url = reverse("assistant_chat")
        self.user = User.objects.create_user(username="seeker", password="test-pass-123")

    def test_requires_login(self):
        response = self.client.post(self.url, {"question": "Hello?"})

        self.assertEqual(response.status_code, 401)

    def test_rejects_get(self):
        self.client.force_login(self.user)

        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_requires_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)

        response = client.post(self.url, {"question": "Hello?"})

        self.assertEqual(response.status_code, 403)

    @patch("assistant.views.answer_question")
    def test_rejects_blank_and_too_long_questions(self, answer):
        self.client.force_login(self.user)

        for question in ["   ", "a" * 501]:
            response = self.client.post(self.url, {"question": question})
            self.assertEqual(response.status_code, 400)

        answer.assert_not_called()

    @override_settings(DEBUG=False)
    @patch("assistant.views.answer_question")
    def test_returns_answer_and_source_titles(self, answer):
        answer.return_value = {"answer": "Yes.", "sources": CHUNKS[:1], "retrieved": CHUNKS}
        self.client.force_login(self.user)

        response = self.client.post(self.url, {"question": " Can I upload DOCX? "})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"answer": "Yes.", "sources": ["File rules"]})
        answer.assert_called_once_with("Can I upload DOCX?")

    @override_settings(DEBUG=True)
    @patch("assistant.views.answer_question")
    def test_debug_includes_retrieved_chunks(self, answer):
        answer.return_value = {"answer": "Yes.", "sources": [], "retrieved": CHUNKS}
        self.client.force_login(self.user)

        data = self.client.post(self.url, {"question": "Hello?"}).json()

        self.assertEqual(data["retrieved"][0]["id"], "help-05")
        self.assertEqual(data["retrieved"][0]["similarity"], 0.585)

    @patch("assistant.views.logger")
    @patch("assistant.views.answer_question", side_effect=DatabaseError("no rag_chunk table"))
    def test_failure_returns_a_friendly_error(self, _answer, _logger):
        self.client.force_login(self.user)

        response = self.client.post(self.url, {"question": "Hello?"})

        self.assertEqual(response.status_code, 503)
        self.assertNotIn("rag_chunk", response.json()["error"])


class WidgetDisplayTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="seeker", password="test-pass-123")

    def test_hidden_from_anonymous_visitors(self):
        self.assertNotContains(self.client.get(reverse("home")), 'id="chat-widget"')

    def test_shown_to_logged_in_users(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("home"))

        self.assertContains(response, 'id="chat-widget"')
        self.assertNotContains(response, 'name="analysis_id"')

    def test_result_page_connects_the_chat_to_its_analysis(self):
        analysis = create_analysis(self.user)
        self.client.force_login(self.user)

        response = self.client.get(reverse("analysis_detail", args=[analysis.id]))

        self.assertContains(response, f'name="analysis_id" value="{analysis.id}"')
        self.assertContains(response, reverse("assistant_history", args=[analysis.id]))
        self.assertContains(response, "About: Backend Developer")

    def test_analysis_without_result_is_not_connected(self):
        analysis = create_analysis(self.user, result_data={})
        self.client.force_login(self.user)

        response = self.client.get(reverse("analysis_detail", args=[analysis.id]))

        self.assertNotContains(response, 'name="analysis_id"')


class AnalysisChatTests(TestCase):
    def setUp(self):
        self.url = reverse("assistant_chat")
        self.user = User.objects.create_user(username="seeker", password="test-pass-123")
        self.other_user = User.objects.create_user(username="other", password="test-pass-123")
        self.analysis = create_analysis(self.user)
        self.client.force_login(self.user)

    @patch("assistant.views.answer_question")
    def test_cannot_use_the_analysis_of_another_user(self, answer):
        other_analysis = create_analysis(self.other_user)

        response = self.client.post(
            self.url,
            {"question": "Show the CV.", "analysis_id": other_analysis.id},
        )

        self.assertEqual(response.status_code, 404)
        answer.assert_not_called()
        self.assertFalse(ChatMessage.objects.exists())

    @patch("assistant.views.answer_question")
    def test_rejects_invalid_analysis_ids(self, answer):
        for analysis_id in ["abc", "-1", "1 OR 1=1", "99999999999999999999999"]:
            response = self.client.post(
                self.url,
                {"question": "Hello?", "analysis_id": analysis_id},
            )
            self.assertEqual(response.status_code, 404)

        answer.assert_not_called()

    @patch("assistant.views.answer_question")
    def test_saves_the_question_and_answer_with_the_analysis(self, answer):
        answer.return_value = {
            "answer": "Learn Docker first.",
            "sources": [],
            "used_analysis": True,
            "retrieved": [],
        }

        response = self.client.post(
            self.url,
            {"question": "What should I learn?", "analysis_id": self.analysis.id},
        )

        self.assertEqual(response.json()["sources"], ["This analysis"])
        answer.assert_called_once_with("What should I learn?", analysis=self.analysis)
        self.assertEqual(
            list(self.analysis.chat_messages.values_list("role", "content")),
            [("user", "What should I learn?"), ("assistant", "Learn Docker first.")],
        )

    @patch("assistant.views.logger")
    @patch("assistant.views.answer_question", side_effect=ValueError("bad reply"))
    def test_failed_answer_saves_nothing(self, _answer, _logger):
        response = self.client.post(
            self.url,
            {"question": "What should I learn?", "analysis_id": self.analysis.id},
        )

        self.assertEqual(response.status_code, 503)
        self.assertFalse(ChatMessage.objects.exists())

    @patch("assistant.views.answer_question")
    def test_chat_without_analysis_saves_nothing(self, answer):
        answer.return_value = {"answer": "Yes.", "sources": [], "retrieved": []}

        self.client.post(self.url, {"question": "Can I upload DOCX?"})

        self.assertFalse(ChatMessage.objects.exists())

    def test_history_returns_only_this_analysis_in_order(self):
        save_exchange(self.analysis, "First?", "First answer.")
        save_exchange(create_analysis(self.user), "Elsewhere?", "Other answer.")

        response = self.client.get(reverse("assistant_history", args=[self.analysis.id]))

        self.assertEqual(
            response.json()["messages"],
            [
                {"role": "user", "content": "First?"},
                {"role": "assistant", "content": "First answer."},
            ],
        )

    def test_history_of_another_user_is_not_found(self):
        other_analysis = create_analysis(self.other_user)
        save_exchange(other_analysis, "Private?", "Private answer.")

        response = self.client.get(reverse("assistant_history", args=[other_analysis.id]))

        self.assertEqual(response.status_code, 404)
        self.assertNotContains(response, "Private", status_code=404)


class AnalysisContextTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="seeker", password="test-pass-123")
        self.analysis = create_analysis(self.user)

    def test_prompt_contains_every_part_of_the_analysis(self):
        prompt = build_user_prompt("What next?", CHUNKS, self.analysis)

        for text in ["Backend Developer", "CV text", "Needs Docker", "Notes", "Learn Docker", "PDF or DOCX.", "What next?"]:
            self.assertIn(text, prompt)

    def test_prompt_without_analysis_has_no_analysis_section(self):
        self.assertNotIn("Current analysis", build_user_prompt("What next?", CHUNKS))

    def test_long_text_is_cut_to_the_limit(self):
        self.analysis.resume.extracted_text = "x" * (MAX_CV_LENGTH + 500)

        self.assertEqual(format_analysis(self.analysis).count("x"), MAX_CV_LENGTH)

    def test_history_keeps_only_the_latest_messages_oldest_first(self):
        for number in range(HISTORY_LIMIT):
            save_exchange(self.analysis, f"Question {number}", f"Answer {number}")

        history = get_history(self.analysis)

        self.assertEqual(len(history), HISTORY_LIMIT)
        self.assertEqual(history[-1], {"role": "assistant", "content": f"Answer {HISTORY_LIMIT - 1}"})
        self.assertEqual(history[0]["role"], "user")

    @patch("assistant.services.generate_answer")
    @patch("assistant.services.retrieve_chunks", return_value=CHUNKS)
    def test_sends_analysis_and_history_to_the_model(self, _retrieve, generate):
        save_exchange(self.analysis, "First?", "First answer.")
        generate.return_value = {"answer": "Yes.", "source_ids": [], "used_analysis": True}

        result = answer_question("And then?", analysis=self.analysis)

        generate.assert_called_once_with(
            "And then?",
            CHUNKS,
            self.analysis,
            [
                {"role": "user", "content": "First?"},
                {"role": "assistant", "content": "First answer."},
            ],
        )
        self.assertTrue(result["used_analysis"])

    @patch("assistant.services.logger")
    @patch("assistant.services.generate_answer", return_value={"answer": "Yes.", "source_ids": []})
    @patch("assistant.services.retrieve_chunks", side_effect=DatabaseError("no rag_chunk table"))
    def test_analysis_chat_still_works_without_help_search(self, _retrieve, generate, _logger):
        result = answer_question("And then?", analysis=self.analysis)

        self.assertEqual(result["answer"], "Yes.")
        self.assertEqual(generate.call_args.args[1], [])

    @patch("assistant.services.retrieve_chunks", side_effect=DatabaseError("no rag_chunk table"))
    def test_help_chat_fails_without_help_search(self, _retrieve):
        with self.assertRaises(DatabaseError):
            answer_question("How do I log in?")
