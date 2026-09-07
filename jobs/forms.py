from django import forms
from .models import JobApplication, JobListing

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication

        fields = [  # no user field to protect against malicious users
            "application_date",
            "company_name",
            "position_name",
            "location",
            "progress_notes",
        ]

        widgets = { # fixed height
            "progress_notes": forms.Textarea(
                attrs={"rows": 6,}
            ),
        }


class JobListingForm(forms.ModelForm):
    class Meta:
        model = JobListing
        # created_by is not allowed to be submitted by the browser
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
