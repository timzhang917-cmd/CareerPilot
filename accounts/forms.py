from django import forms
from django.contrib.auth.forms import UserCreationForm # 内置模块，已提供账密验证功能
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    ACCOUNT_TYPE_CHOICES = [
        ("job_seeker", "Job Seeker"), # 提交给后端的值和显示的文字
        ("hr", "HR / Recruiter"),
    ]

    account_type = forms.ChoiceField( # 必须从选项里选一个
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