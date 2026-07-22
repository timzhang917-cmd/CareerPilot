from pathlib import Path
from django import forms


class AnalysisInputForm(forms.Form):
    resume_file = forms.FileField(label="Resume")

    job_title = forms.CharField(
        label="Job title",
        max_length=200,
    )

    job_description = forms.CharField(
        label="Job description",
        widget=forms.Textarea(attrs={"rows": 8}),
    )

    supplementary_text = forms.CharField(
        label="Supplementary materials",
        required=False,
        widget=forms.Textarea(attrs={"rows": 5}),
    )

    def clean_resume_file(self):
        resume_file = self.cleaned_data["resume_file"]
        extension = Path(resume_file.name).suffix.lower()

        if extension not in {".pdf", ".docx"}:
            raise forms.ValidationError(
                "Only PDF and DOCX files are allowed."
            )

        if resume_file.size > 5 * 1024 * 1024:
            raise forms.ValidationError(
                "The resume file must not exceed 5 MB."
            )

        return resume_file