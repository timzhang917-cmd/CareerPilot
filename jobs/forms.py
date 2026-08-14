from django import forms

from .models import JobApplication, JobListing


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


class JobListingForm(forms.ModelForm):
    class Meta:
        model = JobListing

        # created_by 不允许由浏览器提交，
        # 后续在 view 中强制绑定当前 HR 用户。
        fields = [
            "company_name",
            "industry",
            "job_positions",
            "location",
            "official_url",
        ]

        labels = {
            "company_name": "Company name",
            "industry": "Industry",
            "job_positions": "Job positions",
            "location": "Location",
            "official_url": "Official recruitment URL",
        }

        widgets = {
            "company_name": forms.TextInput(
                attrs={
                    "placeholder": "e.g. Apple",
                }
            ),
            "industry": forms.TextInput(
                attrs={
                    "placeholder": "e.g. Technology",
                }
            ),
            "job_positions": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": (
                        "e.g. Sales Manager / "
                        "Marketing Graduate"
                    ),
                }
            ),
            "location": forms.TextInput(
                attrs={
                    "placeholder": "e.g. Shanghai / Beijing",
                }
            ),
            "official_url": forms.URLInput(
                attrs={
                    "placeholder": "https://jobs.example.com",
                }
            ),
        }
