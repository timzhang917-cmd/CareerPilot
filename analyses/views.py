from django.contrib import messages
from django.shortcuts import redirect, render

from resumes.models import JobDescription, Resume
from resumes.parsers import extract_resume_text

from .forms import AnalysisInputForm
from .models import Analysis


def home(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")

        analysis_form = AnalysisInputForm(
            request.POST,
            request.FILES,
        )

        if analysis_form.is_valid():
            resume = Resume.objects.create(
                user=request.user,
                file=analysis_form.cleaned_data["resume_file"],
            )  # 文件保存到media/resumes,db创建resume记录

            extracted_text = extract_resume_text(resume.file.path) #读取刚才保存的pdf/docx

            resume.extracted_text = extracted_text
            resume.save(update_fields=["extracted_text"])

            job_description = JobDescription.objects.create(
                user=request.user,
                job_title=analysis_form.cleaned_data["job_title"],
                content=analysis_form.cleaned_data["job_description"],
            )

            Analysis.objects.create(
                user=request.user,
                resume=resume,
                job_description=job_description,
                supplementary_text=analysis_form.cleaned_data[
                    "supplementary_text"
                ],
            )

            messages.success(
                request,
                "uploaded successfully",
            )

            return redirect("home")
    else:
        analysis_form = AnalysisInputForm()

    return render(
        request,
        "analyses/home.html",
        {"analysis_form": analysis_form},
    )
