import tempfile
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from resumes.models import JobDescription, Resume

from .ai_models import AI_MODELS
from .models import Analysis

START_PROMPT = "先去启动一次分析，然后再来这里查看反馈吧～"


class CommunityPageTests(TestCase):
    def test_community_page_displays_coming_soon_message(self):
        response = self.client.get(reverse("community"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "analyses/community.html")
        self.assertContains(response, "Coming soon")

    def test_header_links_to_community_page(self):
        response = self.client.get(reverse("home"))

        self.assertContains(
            response,
            f'href="{reverse("community")}"',
        )


class LoggedOutAnalysisPromptTests(TestCase):
    def test_home_displays_login_and_registration_prompt(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="auth-dialog-open"')
        self.assertContains(response, 'id="auth-dialog"')
        self.assertContains(response, f'href="{reverse("login")}"')
        self.assertContains(response, f'href="{reverse("register")}"')

    def test_example_images_open_on_the_current_page(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, 'id="image-dialog"')
        self.assertNotContains(response, 'target="_blank"')


class AnalysisDisplayTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("seeker")
        self.client.force_login(self.user)

    def create_analysis(self, result_data, cv_text="", supplementary_text=""):
        return Analysis.objects.create(
            user=self.user,
            resume=Resume.objects.create(
                user=self.user,
                file="resumes/cv.pdf",
                extracted_text=cv_text,
            ),
            job_description=JobDescription.objects.create(
                user=self.user,
                job_title="Developer",
                content="Build things",
            ),
            supplementary_text=supplementary_text,
            result_data=result_data,
        )

    def get_analysis_page(self, analysis):
        return self.client.get(reverse("analysis_detail", args=[analysis.id]))

    def test_result_page_shows_the_inputs_of_the_analysis(self):
        analysis = self.create_analysis(
            {"overall": {"score": 50}},
            cv_text="Five years of Python",
            supplementary_text="Portfolio notes",
        )

        response = self.get_analysis_page(analysis)

        self.assertContains(response, 'id="input-drawer"')
        self.assertContains(response, "<small>PDF</small>", html=True)
        self.assertContains(response, "Five years of Python")
        self.assertContains(response, "Developer")
        self.assertContains(response, "Build things")
        self.assertContains(response, "Portfolio notes")

    def test_inputs_are_available_when_the_analysis_has_no_result(self):
        analysis = self.create_analysis({}, cv_text="Five years of Python")

        response = self.get_analysis_page(analysis)

        self.assertContains(response, "This analysis has no result")
        self.assertContains(response, "Five years of Python")

    def test_supplementary_entry_is_hidden_when_nothing_was_submitted(self):
        analysis = self.create_analysis({"overall": {"score": 50}})

        response = self.get_analysis_page(analysis)

        self.assertNotContains(response, "Supplementary")

    def test_cv_panel_explains_when_no_text_was_extracted(self):
        analysis = self.create_analysis({"overall": {"score": 50}})

        response = self.get_analysis_page(analysis)

        self.assertContains(response, "No text could be extracted")

    def test_submitted_text_is_escaped(self):
        analysis = self.create_analysis(
            {"overall": {"score": 50}},
            cv_text="<script>alert(1)</script>",
        )

        response = self.get_analysis_page(analysis)

        self.assertNotContains(response, "<script>alert(1)</script>")
        self.assertContains(response, "&lt;script&gt;alert(1)&lt;/script&gt;")

    def test_inputs_are_absent_without_an_analysis(self):
        response = self.client.get(reverse("analysis_result"))

        self.assertNotContains(response, 'id="input-drawer"')

    def test_result_page_without_analysis_shows_start_prompt(self):
        response = self.client.get(reverse("analysis_result"))

        self.assertContains(response, START_PROMPT)

    def test_result_page_hides_analysis_from_an_earlier_session(self):
        self.create_analysis({"overall": {"level": "Old Result", "score": 50}})

        response = self.client.get(reverse("analysis_result"))

        self.assertContains(response, START_PROMPT)
        self.assertNotContains(response, "Old Result")

    def test_history_still_opens_analysis_from_an_earlier_session(self):
        analysis = self.create_analysis(
            {"overall": {"level": "Old Result", "score": 50}}
        )

        response = self.client.get(
            reverse("analysis_detail", args=[analysis.id])
        )

        self.assertContains(response, "Old Result")

    def test_failed_analysis_from_history_explains_the_problem(self):
        analysis = self.create_analysis({})

        response = self.client.get(
            reverse("analysis_detail", args=[analysis.id])
        )

        self.assertContains(response, "This analysis has no result")

    @patch("analyses.views.extract_resume_text", return_value="CV text")
    @patch(
        "analyses.views.call_deepseek",
        return_value={"overall": {"level": "New Result", "score": 80}},
    )
    def test_result_page_shows_analysis_started_in_this_session(self, *mocks):
        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                response = self.client.post(
                    reverse("home"),
                    {
                        "ai_model": "deepseek",
                        "resume_file": SimpleUploadedFile("cv.pdf", b"cv"),
                        "job_title": "Developer",
                        "job_description": "Build things",
                    },
                )

        self.assertRedirects(
            response,
            reverse("analysis_result"),
            fetch_redirect_response=False,
        )
        self.assertContains(
            self.client.get(reverse("analysis_result")),
            "New Result",
        )

    @patch("analyses.views.extract_resume_text", return_value="CV text")
    # autospec fails the test if the view and the function signatures stop matching
    @patch("analyses.views.call_openai", autospec=True, return_value={"overall": {"score": 80}})
    @patch("analyses.views.call_deepseek", autospec=True, return_value={"overall": {"score": 80}})
    def test_each_model_option_calls_its_model(self, call_deepseek, call_openai, _extract):
        cases = [
            ("deepseek", call_deepseek, "max"),
            ("deepseek-flash", call_deepseek, "high"),
            ("openai", call_openai, "high"),
            ("openai-astra", call_openai, "high"),
        ]

        self.assertEqual({case[0] for case in cases}, set(AI_MODELS))

        for choice, expected_call, expected_effort in cases:
            call_deepseek.reset_mock()
            call_openai.reset_mock()

            with tempfile.TemporaryDirectory() as media_root:
                with override_settings(MEDIA_ROOT=media_root):
                    self.client.post(
                        reverse("home"),
                        {
                            "ai_model": choice,
                            "resume_file": SimpleUploadedFile("cv.pdf", b"cv"),
                            "job_title": "Developer",
                            "job_description": "Build things",
                        },
                    )

            expected_call.assert_called_once()
            self.assertEqual(
                expected_call.call_args.args[-2:],
                (AI_MODELS[choice]["model"], expected_effort),
            )
            self.assertEqual(call_deepseek.call_count + call_openai.call_count, 1)

    def test_form_offers_every_configured_model(self):
        response = self.client.get(reverse("home"))

        for key, config in AI_MODELS.items():
            self.assertContains(response, f'<option value="{key}"')
            self.assertContains(response, config["label"])

    def test_result_page_ignores_analysis_of_another_user(self):
        other_user = User.objects.create_user("other")
        analysis = Analysis.objects.create(
            user=other_user,
            resume=Resume.objects.create(user=other_user, file="resumes/cv.pdf"),
            job_description=JobDescription.objects.create(
                user=other_user,
                job_title="Developer",
                content="Build things",
            ),
            result_data={"overall": {"level": "Private Result", "score": 50}},
        )
        session = self.client.session
        session["latest_analysis_id"] = analysis.id
        session.save()

        response = self.client.get(reverse("analysis_result"))

        self.assertNotContains(response, "Private Result")
        self.assertNotContains(response, 'id="input-drawer"')

    def test_history_displays_a_score_of_zero(self):
        self.create_analysis({"overall": {"score": 0}})

        response = self.client.get(reverse("analysis_history"))

        self.assertContains(response, "0%")

    def test_history_displays_a_dash_when_score_is_missing(self):
        self.create_analysis({})

        response = self.client.get(reverse("analysis_history"))

        self.assertContains(response, "—")
        self.assertNotContains(response, "%")

    def test_header_marks_the_current_page(self):
        response = self.client.get(reverse("analysis_history"))

        self.assertContains(response, 'aria-current="page"', count=1)

