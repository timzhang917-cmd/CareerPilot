from django.shortcuts import render

from .models import JobListing


def job_search(request):
    # 从数据库中读取全部岗位信息
    job_listings = JobListing.objects.all()

    # 把岗位数据交给前端 HTML
    return render(
        request,
        "jobs/main.html",
        {"job_listings": job_listings},
    )
