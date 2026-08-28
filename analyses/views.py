from .services import call_deepseek, call_openai
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from resumes.models import JobDescription, Resume
from resumes.parsers import extract_resume_text

from .forms import AnalysisInputForm
from .models import Analysis


def home(request): #控制首页和分析流程

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")

        analysis_form = AnalysisInputForm(
            request.POST,
            request.FILES,
        ) # 创建一个表单

        if analysis_form.is_valid():

            resume = Resume.objects.create( # 执行数据库insert
                user=request.user,
                file=analysis_form.cleaned_data["resume_file"],
            )  #创建数据库记录，但是提取建立文本字段暂时为空等待提取

            extracted_text = extract_resume_text(resume.file.path) # 提取文本

            resume.extracted_text = extracted_text # 把刚提取出来的文本写入数据库模型对象的extracted_text字段
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

            # 两个函数接收相同参数，并返回相同结构的 JSON 字典
            analysis_result_data = call_model(
                resume.extracted_text,
                job_description.job_title,
                job_description.content,
                analysis.supplementary_text,
            )

            # JSONField 可以直接保存 Python 字典
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

@login_required
def analysis_result(request, analysis_id=None):
    # 没有analyseid时展示最新结果，有id时作为历史记录呈现

    if analysis_id is None:
        analysis = (
            Analysis.objects
            .filter(user=request.user)
            .order_by("-created_at")
            .first()
        )
    else:
        # 检查id和所属用户，防偷窥
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
def analysis_history(request): # 显示历史信息

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
