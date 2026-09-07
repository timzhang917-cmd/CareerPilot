"""
AI Usage Declaration:
-This file contains code generated with help of AI tools.
-Tool Used: ChatGPT
-Date Generated: 2026-08
-ChatGPT was used to assist with the deletion, editing, and current-user ownership validation logic in my_applications().
 It was also used to handle different separators in split_options().

I have reviewed, tested, and understood the AI-generated code.
"""

from datetime import date
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .forms import JobApplicationForm, JobListingForm
from .models import JobApplication, JobListing

def split_options(values):
    # divide multiple items into separate options, e.g. shanghai/beijing/ -> shanghai, beijing
    options = set()

    for value in values:
        # compatible with different separators that administrators may use
        normalized_value = (
            value.replace("／", "/")
                 .replace("、", "/")
                 .replace(",", "/")
        )

        for item in normalized_value.split("/"):
            item = item.strip()

            if item:
                options.add(item)

    return sorted(options)


def job_search(request): # show job listings based on user filtering

    job_listings = JobListing.objects.all() # read all job listings

    selected_company = request.GET.get("company", "")
    selected_position = request.GET.get("position", "")
    selected_location = request.GET.get("location", "")
    selected_industry = request.GET.get("industry", "")

    # filtering is only applied if the user has selected a specific condition
    if selected_company:
        job_listings = job_listings.filter(
            company_name__icontains=selected_company
        )

    if selected_position:
        job_listings = job_listings.filter(
            job_positions__icontains=selected_position
        )

    if selected_location:
        job_listings = job_listings.filter(
            location__icontains=selected_location
        )

    if selected_industry:
        job_listings = job_listings.filter(
            industry__icontains=selected_industry
        )

    industry_options = (
        JobListing.objects
        .values_list("industry", flat=True)
        .distinct()
        .order_by("industry")
    )

    # a field may contain multiple positions, so it needs to be split
    position_values = JobListing.objects.values_list(
        "job_positions",
        flat=True,
    )
    position_options = split_options(position_values)

    # a field may contain multiple locations, so it needs to be split
    location_values = JobListing.objects.values_list(
        "location",
        flat=True,
    )
    location_options = split_options(location_values)

    context = {
        # job listings after filtering
        "job_listings": job_listings,
        "active_tab": "search",

        # 3 select boxes
        "position_options": position_options,
        "location_options": location_options,
        "industry_options": industry_options,

        "selected_company": selected_company,
        "selected_position": selected_position,
        "selected_location": selected_location,
        "selected_industry": selected_industry,
    }

    return render(
        request,
        "jobs/main.html",
        context,
    )


@login_required
def my_applications(request): 

    open_application_modal = False
    editing_application = None

    if request.method == "POST":
        action = request.POST.get("action")
        application_id = request.POST.get("application_id") 

        # delete operation: backend also checks if the record belongs to the current logged-in user
        if action == "delete" and application_id:
            application = get_object_or_404(
                JobApplication,
                id=application_id,
                user=request.user,
            )
            application.delete()

            return redirect("my_applications")

        if application_id: # id is only present when editing an existing record
            editing_application = get_object_or_404(
                JobApplication,
                id=application_id,
                user=request.user,
            )

        form = JobApplicationForm( # update if instance exists or create new one
            request.POST,
            instance=editing_application,
        )

        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user # ensure it is from current user
            application.save()

            return redirect("my_applications")  # jump to application page after add or edit

        open_application_modal = True
    else:
        form = JobApplicationForm(
            initial={
                "application_date": date.today(),
            }
        )

    applications = (
        JobApplication.objects
        .filter(user=request.user)
        .order_by("-application_date", "-created_at")
    )

    return render(
        request,
        "jobs/main.html",
        {
            "applications": applications,
            "form": form,
            "editing_application": editing_application,
            "open_application_modal": open_application_modal,
            "active_tab": "applications",
        },
    )

@login_required
def hr_dashboard(request): 

    is_hr = request.user.groups.filter(name="HR",).exists()
    # job seekers cannot access HR dashboard
    if not is_hr and not request.user.is_superuser:
        raise PermissionDenied("This page is only available to HR users.")

    open_job_post_modal = False

    if request.method == "POST":
        action = request.POST.get("action")

        # delete operation
        if action == "delete":
            job_id = request.POST.get("job_id")

            # backend also checks if the record belongs to the current logged-in user
            job_listing = get_object_or_404(
                JobListing,
                id=job_id,
                created_by=request.user,
            )

            job_listing.delete()

            return redirect("hr_dashboard")

        form = JobListingForm(request.POST)

        if form.is_valid():
            job_listing = form.save(commit=False)
            job_listing.created_by = request.user # bind HR identity before saving
            job_listing.save()

            # avoid duplicate submission after refreshing the page
            return redirect("hr_dashboard")

        # open modal again if form validation fails
        open_job_post_modal = True
    else:
        form = JobListingForm()

    # only read the job listings created by the current HR user.
    job_listings = (
        JobListing.objects
        .filter(created_by=request.user)
        .order_by("-id")
    )

    return render(
        request,
        "jobs/hr_dashboard.html",
        {
            "form": form,
            "job_listings": job_listings,
            "open_job_post_modal": open_job_post_modal,
        },
    )