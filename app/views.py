from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse

from app.models import Job

#########################################################################################################
################################################ MAIN PAGE ##############################################
#########################################################################################################


# the main page
def index(request):
    filter = get_job_filter(request.session)

    job = Job.objects.filter(status=filter['status']).first()
    job_count = Job.objects.filter(status=filter['status']).count()

    context = {"job": job, "job_count": job_count, "filter": filter}
    return HttpResponse(render(request, "jobs/index.html", context))


# when the user filters all jobs by status from main page
def status_filter(request, status):
    if (not valid_status(status)):
        return HttpResponseRedirect(reverse("jobs:index"))

    request.session['status_filter'] = status
    return HttpResponseRedirect(reverse("jobs:index"))


#########################################################################################################
################################################ TITLES PAGE ############################################
#########################################################################################################


# the titles page
def titles(request):
    jobs = Job.objects.order_by("title").filter(status="new")
    jobs_size = jobs.count()
    return HttpResponse(render(request, "jobs/titles.html", {"jobs": jobs, "jobs_size": jobs_size}))


#########################################################################################################
################################################ COMMON #################################################
#########################################################################################################


# update status of a single job from any page
def update_status(request, job_id):
    status = request.POST["status"]
    next = request.POST["next"]

    if (not valid_status(status)):
        return HttpResponseRedirect(reverse(next))

    job = get_object_or_404(Job, pk=job_id)
    job.status = status
    job.save()
    return HttpResponseRedirect(reverse(next))


#########################################################################################################
################################################ HELPERS ################################################
#########################################################################################################

# sets up job filtering for the main job page
def get_job_filter(session):
    company_search: str = session['company_search'] if 'company_search' in session else ""
    title_search: str = session['title_search'] if 'title_search' in session else ""
    text_search: str = session['text_search'] if 'text_search' in session else ""
    status_filter: str = session['status_filter'] if 'status_filter' in session else "new"

    filter = {
        'companies': [company.strip().lower() for company in company_search.split(",")],
        'titles': [title.strip().lower() for title in title_search.split(",")],
        'text': [text.strip().lower() for text in text_search.split(",")],
        'status': status_filter
    }
    return filter


# the only set of valid statuses
def valid_status(status):
    return status in ["new", "declined", "interested", "later", "applied", "interviewing", "offer", "rejected"]
