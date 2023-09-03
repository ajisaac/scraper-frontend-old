from django.db import models


class Job(models.Model):
    id = models.BigAutoField(primary_key=True)
    # job title
    title = models.TextField(blank=True, null=True)
    # url of job posting
    url = models.TextField(blank=True, null=True)
    # company name
    company = models.TextField(blank=True, null=True)
    # miscelanious info
    subtitle = models.TextField(blank=True, null=True)
    # job description in html
    description = models.TextField(blank=True, null=True)
    # the search term for job if applicable
    search_term = models.TextField(blank=True, null=True)
    # the status of the job
    status = models.TextField(blank=True, null=True)
    # where is the job located
    location = models.TextField(blank=True, null=True)
    # which site did the job come from
    job_site = models.TextField(blank=True, null=True)
    # job posting date if available
    job_posting_date = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'jobs'

    __str__ = lambda self: f"{self.title} - {self.company}"
