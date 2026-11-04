from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class LoginRedirectTests(TestCase):
    def setUp(self):
        self.credentials = {"username": "seeker", "password": "correct-horse-battery"}
        User.objects.create_user(**self.credentials)

    def login(self, next_url):
        return self.client.post(
            f"{reverse('login')}?next={next_url}",
            self.credentials,
        )

    def test_login_returns_to_requested_page(self):
        response = self.login(reverse("analysis_history"))

        self.assertRedirects(
            response,
            reverse("analysis_history"),
            fetch_redirect_response=False,
        )

    def test_login_ignores_next_url_on_another_site(self):
        response = self.login("https://example.com/")

        self.assertRedirects(
            response,
            reverse("home"),
            fetch_redirect_response=False,
        )
