from django.conf import settings
from django.db import models

class JobListing(models.Model): # hr发布的岗位信息
   
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_listings",
        null=True,
        blank=True,  # 允许为空，用来兼容以前由管理员录入的招聘信息。
    )
    company_name = models.CharField(max_length=200)
    industry = models.CharField(max_length=200)
    job_positions = models.TextField()
    location = models.CharField(max_length=200)
    official_url = models.URLField()

    def __str__(self):
        return self.company_name


class JobApplication(models.Model): # 用户自己的管理记录
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_applications",
    )

    application_date = models.DateField()
    company_name = models.CharField(max_length=200)
    position_name = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True,)
    progress_notes = models.TextField(blank=True) # 更新进展

    # 记录创建和最后修改时间
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company_name} - {self.position_name}"