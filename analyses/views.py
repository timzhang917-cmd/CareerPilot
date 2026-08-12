from .services import call_deepseek
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from resumes.models import JobDescription, Resume
from resumes.parsers import extract_resume_text

from .forms import AnalysisInputForm
from .models import Analysis
from .sample import SAMPLE_ANALYSIS_RESULT


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

            analysis = Analysis.objects.create(
                user=request.user,
                resume=resume,
                job_description=job_description,
                supplementary_text=analysis_form.cleaned_data[
                    "supplementary_text"
                ],
            )

            # 调用模型并取得已经解析完成的 JSON 字典
            analysis_result_data = call_deepseek(
                resume.extracted_text,
                job_description.job_title,
                job_description.content,
                analysis.supplementary_text,
            )

            # JSONField 可以直接保存 Python 字典
            analysis.result_data = analysis_result_data

            analysis.status = Analysis.Status.COMPLETED
            analysis.save()

            return redirect("analysis_result")
    
    else:
        analysis_form = AnalysisInputForm()

    return render(
        request,
        "analyses/home.html",
        {"analysis_form": analysis_form},
    )

@login_required
def analysis_result(request, analysis_id=None):
    """
    不传 analysis_id：显示当前用户最新一次分析。
    传入 analysis_id：显示当前用户指定的一次历史分析。
    """

    if analysis_id is None:
        analysis = (
            Analysis.objects
            .filter(user=request.user)
            .order_by("-created_at")
            .first()
        )
    else:
        # 同时检查记录编号和所属用户，防止查看别人的记录
        analysis = get_object_or_404(
            Analysis,
            id=analysis_id,
            user=request.user,
        )

    # 默认使用样本数据，保证旧测试记录不会破坏页面
    result = SAMPLE_ANALYSIS_RESULT
    analysis_text = ""

    if analysis:
        saved_result = analysis.result_data or {}

        # 新版结构化 JSON 包含 overall，因此直接交给前端展示
        if "overall" in saved_result:
            result = saved_result

        # 兼容以前保存的纯文本分析记录
        else:
            analysis_text = saved_result.get(
                "analysis_text",
                "",
            )

    return render(
        request,
        "analyses/result.html",
        {
            "analysis": analysis,
            "analysis_text": analysis_text,
            "result": result,
            "active_tab": "result",
        },
    )


@login_required
def analysis_history(request):
    """显示当前登录用户的全部历史分析记录。"""

    analyses = (
        Analysis.objects
        .filter(user=request.user)
        .select_related("job_description")
        .order_by("-created_at")
    )

    return render(
        request,
        "analyses/history.html",
        {
            "analyses": analyses,
            "active_tab": "history",
        },
    )
