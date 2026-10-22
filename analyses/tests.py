from django.test import TestCase
from django.urls import reverse


class CommunityPageTests(TestCase):
    def test_community_page_displays_coming_soon_message(self):
        response = self.client.get(reverse("community"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "analyses/community.html")
        self.assertContains(response, "开发中，敬请期待")

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
