"""
AI Usage Declaration:
-This file contains code generated with help of AI tools.
-Tool Used: ChatGPT
-Date Generated: 2026-08
-ChatGPT was used to define clean_resume_file() (line 44-58)

I have reviewed, tested, and understood the AI-generated code.
"""


from pathlib import Path
from django import forms

from .ai_models import AI_MODELS, DEFAULT_AI_MODEL

class AnalysisInputForm(forms.Form): 
# resume and job description input form for AI analysis

    ai_model = forms.ChoiceField(
        label="AI model",
        choices=[(key, config["label"]) for key, config in AI_MODELS.items()],
        initial=DEFAULT_AI_MODEL,
    )
    
    resume_file = forms.FileField(label="CV")

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

    def clean_resume_file(self):  # validate the uploaded resumes
        resume_file = self.cleaned_data["resume_file"]
        extension = Path(resume_file.name).suffix.lower()

        if extension not in {".pdf", ".docx"}:
            raise forms.ValidationError(
                "Only PDF and DOCX files are allowed."
            )

        if resume_file.size > 5 * 1024 * 1024:
            raise forms.ValidationError(
                "The CV file must not exceed 5 MB."
            )

        return resume_file