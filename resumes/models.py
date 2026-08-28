from django.conf import settings
from django.db import models


class Resume(models.Model):  #继承Django自带的model类，里面有user，外键等属性
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resumes",
    )
    file = models.FileField(upload_to="resumes/")
    extracted_text = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.file.name}"


class JobDescription(models.Model): # 一次分析除了简历，还需要结合岗位jd一起，所以要单独建类
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_descriptions",
    )
    job_title = models.CharField(max_length=200)
    content = models.TextField() #不能为空
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.job_title}"
