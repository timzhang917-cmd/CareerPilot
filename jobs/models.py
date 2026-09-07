from django.conf import settings
from django.db import models

class JobListing(models.Model): 
   
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_listings",
        null=True,
        blank=True,  # blank is allowed, for compatibility with previously entered job information by administrators.
    )
    company_name = models.CharField(max_length=200)
    industry = models.CharField(max_length=200)
    job_positions = models.TextField()
    location = models.CharField(max_length=200)
    official_url = models.URLField()

    def __str__(self):
        return self.company_name


class JobApplication(models.Model): 
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_applications",
    )

    application_date = models.DateField()
    company_name = models.CharField(max_length=200)
    position_name = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True,)
    progress_notes = models.TextField(blank=True) 

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company_name} - {self.position_name}"