from django.conf import settings
from django.db import models


class Analysis(models.Model): # 一条AI分析记录

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="analyses",
    )
    resume = models.ForeignKey(
        "resumes.Resume",
        on_delete=models.CASCADE,
        related_name="analyses",
    )
    job_description = models.ForeignKey(
        "resumes.JobDescription",
        on_delete=models.CASCADE,
        related_name="analyses",
    )
    supplementary_text = models.TextField(blank=True)
    result_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analysis {self.id} - {self.user.username}"