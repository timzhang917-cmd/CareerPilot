from django.conf import settings
from django.db import models


class JobListing(models.Model):

    company_name = models.CharField(max_length=200)

    # 所属行业
    industry = models.CharField(max_length=200)

    # 招聘岗位，可以填写多个岗位名称
    job_positions = models.TextField()

    # 工作地点，可以填写多个地点
    location = models.CharField(max_length=200)

    # 官网链接
    official_url = models.URLField()

    def __str__(self):
        return self.company_name


class JobApplication(models.Model):
    # 这条投递记录属于哪个用户
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_applications",
    )

    # 用户实际投递简历的日期
    application_date = models.DateField()

    # 公司和岗位信息
    company_name = models.CharField(max_length=200)
    position_name = models.CharField(max_length=200)

    # 工作地点可以不填
    location = models.CharField(
        max_length=200,
        blank=True,
    )

    # 用户自由记录投递、面试和后续进展
    progress_notes = models.TextField(blank=True)

    # 记录创建和最后修改时间
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company_name} - {self.position_name}"
