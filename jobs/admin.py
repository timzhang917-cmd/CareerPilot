from django.contrib import admin

from .models import JobApplication, JobListing


admin.site.register(JobListing)
admin.site.register(JobApplication)
