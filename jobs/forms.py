from django import forms
from .models import JobApplication, JobListing

class JobApplicationForm(forms.ModelForm): # 申请记录新建和编辑
    class Meta:
        model = JobApplication

        fields = [  # 少了user起到保护效果
            "application_date",
            "company_name",
            "position_name",
            "location",
            "progress_notes",
        ]

        widgets = { # 固定高度
            "progress_notes": forms.Textarea(
                attrs={"rows": 6,}
            ),
        }


class JobListingForm(forms.ModelForm):
    class Meta:
        model = JobListing
        # created_by 不允许由浏览器提交
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
            "job_positions": forms.Textarea(
                attrs={
                    "rows": 4,
                }
            ),
        }
