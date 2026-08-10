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
