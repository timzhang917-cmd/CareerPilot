from datetime import date

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import JobApplicationForm
from .models import JobApplication, JobListing


def split_options(values):
    """
    把数据库中的多项文本拆成独立选项。

    例如：
    上海/北京/深圳 -> 上海、北京、深圳
    销售、售前、渠道经理 -> 销售、售前、渠道经理
    """
    options = set()

    for value in values:
        # 兼容管理员可能使用的不同分隔符
        normalized_value = (
            value.replace("／", "/")
                 .replace("、", "/")
                 .replace("，", "/")
                 .replace(",", "/")
        )

        for item in normalized_value.split("/"):
            item = item.strip()

            if item:
                options.add(item)

    # 转换成排序后的列表，方便前端稳定显示
    return sorted(options)


def job_search(request):
    # 先读取全部岗位信息
    job_listings = JobListing.objects.all()

    # 读取用户在 URL 中选择的筛选条件
    selected_company = request.GET.get("company", "")
    selected_position = request.GET.get("position", "")
    selected_location = request.GET.get("location", "")
    selected_industry = request.GET.get("industry", "")

    # 只有用户选择了某项条件时，才进行对应筛选
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

    # 行业直接作为完整选项，不进行拆分
    industry_options = (
        JobListing.objects
        .values_list("industry", flat=True)
        .distinct()
        .order_by("industry")
    )

    # 一个字段中可能包含多个岗位，因此需要拆分
    position_values = JobListing.objects.values_list(
        "job_positions",
        flat=True,
    )
    position_options = split_options(position_values)

    # 一个字段中可能包含多个工作地点，因此需要拆分
    location_values = JobListing.objects.values_list(
        "location",
        flat=True,
    )
    location_options = split_options(location_values)

    context = {
        # 筛选后的岗位信息
        "job_listings": job_listings,
        "active_tab": "search",

        # 三个下拉框的可选内容
        "position_options": position_options,
        "location_options": location_options,
        "industry_options": industry_options,

        # 保存用户当前选择，避免刷新后恢复为空
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
    """展示当前用户的投递记录，并接收弹窗提交的新增或编辑。"""
    open_application_modal = False
    editing_application = None

    if request.method == "POST":
        action = request.POST.get("action")
        application_id = request.POST.get("application_id")

        # 删除操作：后端同时校验记录属于当前登录用户
        if action == "delete" and application_id:
            application = get_object_or_404(
                JobApplication,
                id=application_id,
                user=request.user,
            )
            application.delete()

            return redirect("my_applications")

        if application_id:
            # 只有记录本人可以编辑这条投递信息
            editing_application = get_object_or_404(
                JobApplication,
                id=application_id,
                user=request.user,
            )

        # 有 instance 时更新原记录；没有时创建新记录
        form = JobApplicationForm(
            request.POST,
            instance=editing_application,
        )

        if form.is_valid():
            # user 不由浏览器提交，后端强制绑定当前登录用户
            application = form.save(commit=False)
            application.user = request.user
            application.save()

            return redirect("my_applications")

        # 校验失败时重新打开弹窗，让用户看到错误信息
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
