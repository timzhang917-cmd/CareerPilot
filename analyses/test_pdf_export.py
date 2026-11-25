import json
from io import BytesIO
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from pypdf import PdfReader

from resumes.models import JobDescription, Resume

from .models import Analysis


class AnalysisPdfTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("pdf-owner")
        self.client.force_login(self.user)
        self.example = json.loads(
            Path(__file__).with_name("json_example.json").read_text(encoding="utf-8")
        )

    def create_analysis(self, result, job_title="Software Engineer"):
        return Analysis.objects.create(
            user=self.user,
            resume=Resume.objects.create(
                user=self.user, file="resumes/cv.pdf", extracted_text="Private resume input",
            ),
            job_description=JobDescription.objects.create(
                user=self.user, job_title=job_title, content="Private job description input",
            ),
            supplementary_text="Private supplementary input",
            result_data=result,
        )

    def test_download_available_on_current_and_historical_result(self):
        analysis = self.create_analysis(self.example)
        url = reverse("analysis_pdf", args=[analysis.id])
        session = self.client.session
        session["latest_analysis_id"] = analysis.id
        session.save()

        for page in (reverse("analysis_result"), reverse("analysis_detail", args=[analysis.id])):
            with self.subTest(page=page):
                self.assertContains(self.client.get(page), f'href="{url}"')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/pdf")
        self.assertEqual(
            response.headers["Content-Disposition"],
            f'attachment; filename="CareerPilot-Analysis-{analysis.id}.pdf"',
        )
        self.assertIn("no-store", response.headers["Cache-Control"])

        pdf = PdfReader(BytesIO(b"".join(response.streaming_content)))
        report = " ".join(" ".join(page.extract_text().split()) for page in pdf.pages)
        for content in (
            "Software Engineer", "72%", "78%", "70%", "65%", "80%", "Good Match",
            "Overall Summary", "Key Strengths", "Main Gaps", "Job Requirement Comparison",
            "Must-fix Issues", "Advanced Suggestions",
        ):
            self.assertIn(content, report)
        for key in ("strengths", "gaps"):
            for item in self.example[key]:
                self.assertIn(item, report)
        for key in ("requirements", "must_fix_issues", "suggestions"):
            for item in self.example[key]:
                for value in item.values():
                    self.assertIn(value, report)
        self.assertNotIn("Private resume input", report)
        self.assertNotIn("Private job description input", report)
        self.assertNotIn("Private supplementary input", report)

    def test_chinese_long_text_and_zero_score_survive_export(self):
        analysis = self.create_analysis(
            {
                "overall": {"score": 0, "summary": "可通过项目经历补充相关技能。"},
                "requirements": [{
                    "requirement": "熟悉 Python 和 Django",
                    "evidence": "已有相关项目经验，建议补充可验证的成果。" * 220 + "证据到此为止。",
                    "assessment": "Strong Match",
                }],
                "suggestions": [{"recommendation": "保留原文中的 <tag> & 标点。"}],
            },
            job_title="后端开发工程师",
        )
        response = self.client.get(reverse("analysis_pdf", args=[analysis.id]))
        pdf = PdfReader(BytesIO(b"".join(response.streaming_content)))
        self.assertGreater(len(pdf.pages), 1)
        pages = [page.extract_text() for page in pdf.pages]
        report = "".join("".join(page.split()) for page in pages)
        self.assertIn("后端开发工程师", report)
        self.assertIn("0%", report)
        self.assertIn("证据到此为止。", report)
        self.assertIn("保留原文中的<tag>&标点。", report)
        for number, page in enumerate(pages, start=1):
            self.assertIn(f"Page {number}", page)

    def test_download_hidden_and_unavailable_without_result(self):
        analysis = self.create_analysis({})
        url = reverse("analysis_pdf", args=[analysis.id])

        self.assertNotContains(self.client.get(reverse("analysis_result")), "Download PDF")
        page = self.client.get(reverse("analysis_detail", args=[analysis.id]))
        self.assertNotContains(page, "Download PDF")
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_download_requires_ownership(self):
        analysis = self.create_analysis(self.example)
        url = reverse("analysis_pdf", args=[analysis.id])
        self.client.force_login(get_user_model().objects.create_user("other-user"))
        self.assertEqual(self.client.get(url).status_code, 404)

        self.client.logout()
        self.assertRedirects(
            self.client.get(url), reverse("login") + f"?next={url}",
            fetch_redirect_response=False,
        )
