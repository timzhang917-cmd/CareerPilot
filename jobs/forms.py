from django import forms

from .models import JobApplication


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication

        # 这里专门不写user，因为不能让用户选择记录从而访问别的user的记录
        fields = [
            "application_date",
            "company_name",
            "position_name",
            "location",
            "progress_notes",
        ]

        # 调整浏览器显示的输入控件
        widgets = {
            "application_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "company_name": forms.TextInput(
                attrs={
                    "placeholder": "e.g. Apple",
                }
            ),
            "position_name": forms.TextInput(
                attrs={
                    "placeholder": "e.g. Sales Manager",
                }
            ),
            "location": forms.TextInput(
                attrs={
                    "placeholder": "e.g. Los Angeles",
                }
            ),
            "progress_notes": forms.Textarea(
                attrs={
                    "rows": 6,
                    "placeholder": (
                        "8.13 Submitted resume\n"
                        "8.20 Completed first interview"
                    ),
                }
            ),
        }