from django import forms
from django.contrib.auth.forms import UserCreationForm # build-in module, already provides account and password validation functionality
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    ACCOUNT_TYPE_CHOICES = [
        ("job_seeker", "Job Seeker"), # value for backend , string for frontend
        ("hr", "HR / Recruiter"),
    ]

    account_type = forms.ChoiceField( # must choose from the options
        label="Account type",
        choices=ACCOUNT_TYPE_CHOICES,
        initial="job_seeker",
        widget=forms.RadioSelect,
    )

    class Meta:
        model = User
        fields = ["username"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update(
            {
                "placeholder": "Enter a username",
                "autocomplete": "username",
            }
        )

        self.fields["password1"].widget.attrs.update(
            {
                "placeholder": "Create a password",
                "autocomplete": "new-password",
            }
        )

        self.fields["password2"].widget.attrs.update(
            {
                "placeholder": "Confirm your password",
                "autocomplete": "new-password",
            }
        )