"""
AI Usage Declaration:
-This file contains code generated with help of AI tools.
-Tool Used: ChatGPT
-Date Generated: 2026-08
-ChatGPT was used to assist with refactoring the home() and analysis_result()
During the early stages, the author designed and implemented the core workflow, 
including CV upload/text extraction/model calling
As support for second model and analysis history was introduced, 
the author encountered difficulties in organising existing logic. 
AI assistance was therefore used to refactor these two main functions.

I have reviewed, tested, and understood the AI-generated code.
"""


from .services import call_deepseek, call_openai
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from resumes.models import JobDescription, Resume
from resumes.parsers import extract_resume_text

from .forms import AnalysisInputForm
from .models import Analysis


def home(request): # manage homepage and analysis workflow

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")

        analysis_form = AnalysisInputForm(
            request.POST,
            request.FILES,
        ) # create a form

        if analysis_form.is_valid():

            resume = Resume.objects.create( # execute database insert
                user=request.user,
                file=analysis_form.cleaned_data["resume_file"],
            )  # create database record, but the extracted text field is temporarily empty and waiting to be extracted

            extracted_text = extract_resume_text(resume.file.path) # extract text

            resume.extracted_text = extracted_text # write the extracted text into the extracted_text field of the database model object
            resume.save()

            job_description = JobDescription.objects.create(
                user=request.user,
                job_title=analysis_form.cleaned_data["job_title"],
                content=analysis_form.cleaned_data["job_description"],
            )

            analysis = Analysis.objects.create(
                user=request.user,
                resume=resume,
                job_description=job_description,
                supplementary_text=analysis_form.cleaned_data["supplementary_text"],
            )

            selected_model = analysis_form.cleaned_data["ai_model"] # model choice

            if selected_model == "openai":
                call_model = call_openai
            else:
                call_model = call_deepseek

            # two functions receive the same parameters 
            # and return the same structure of JSON dict
            analysis_result_data = call_model(
                resume.extracted_text,
                job_description.job_title,
                job_description.content,
                analysis.supplementary_text,
            )

            # JSONField can store a Python dict directly
            analysis.result_data = analysis_result_data
            analysis.save()

            return redirect("analysis_result")
    
    else:
        analysis_form = AnalysisInputForm()

    return render(
        request,
        "analyses/home.html",
        {"analysis_form": analysis_form},
    )


def community(request):
    return render(request, "analyses/community.html")

@login_required
def analysis_result(request, analysis_id=None):
    # display latest result without id, display historical record with id

    if analysis_id is None:
        analysis = (
            Analysis.objects
            .filter(user=request.user)
            .order_by("-created_at")
            .first()
        )
    else:
        # check id and user to prevent peeking
        analysis = get_object_or_404(
            Analysis,
            id=analysis_id,
            user=request.user,
        )

    result = analysis.result_data if analysis else {}

    return render(
        request,
        "analyses/result.html",
        {
            "analysis": analysis,
            "result": result,
            "active_tab": "result",
        },
    )


@login_required
def analysis_history(request): # display historical information

    analyses = (
        Analysis.objects
        .filter(user=request.user)
        .select_related("job_description")
        .order_by("-created_at")
    )

    return render(request,
        "analyses/history.html",
        {
        "analyses": analyses,
        "active_tab": "history",
        },
    )
