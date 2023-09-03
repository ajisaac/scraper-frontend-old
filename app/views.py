from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse

from app.models import Job

#########################################################################################################
################################################ MAIN PAGE ##############################################
#########################################################################################################


# the main page
def index(request):
    filter = index__get_job_filter(request.session)
    search_filter = {
        'company_search': request.session['company_search'] if 'company_search' in request.session else "",
        'title_search': request.session['title_search'] if 'title_search' in request.session else "",
        'text_search': request.session['text_search'] if 'text_search' in request.session else "",
    }

    jobs = None
    if (filter['status'] == "new"):
        jobs = [Job.objects.filter(status=filter['status']).first()]
    else:
        jobs = Job.objects.filter(status=filter['status'])[:10]

    job_count = Job.objects.filter(status=filter['status']).count()

    context = {"jobs": jobs, "job_count": job_count,
               "search_filter": search_filter, "filter": filter}

    return HttpResponse(render(request, "jobs/index.html", context))


# when the user filters all jobs by status from main page
def main__status_filter(request, status):
    if (not valid_status(status)):
        return HttpResponseRedirect(reverse("jobs:index"))

    request.session['status_filter'] = status
    return HttpResponseRedirect(reverse("jobs:index"))


def main__filter_search(request):
    request.session['company_search'] = request.POST["company_search"] if "company_search" in request.POST else ""
    request.session['title_search'] = request.POST["title_search"] if "title_search" in request.POST else ""
    request.session['text_search'] = request.POST["text_search"] if "text_search" in request.POST else ""
    return HttpResponseRedirect(reverse("jobs:index"))

#########################################################################################################
################################################ TITLES PAGE ############################################
#########################################################################################################


# the titles page
def titles(request):
    title_search: str = request.session['title_search'] if 'title_search' in request.session else ""
    print(title_search)

    jobs = Job.objects.order_by("title").filter(status="new")
    if (title_search != ""):
        jobs = jobs.filter(title__icontains=title_search)

    jobs_size = jobs.count()

    context = {"jobs": jobs, "jobs_size": jobs_size,
               "title_search": title_search}

    return HttpResponse(render(request, "jobs/titles.html", context))


def titles_title_search(request):
    request.session['title_search'] = request.POST["title_search"]
    return HttpResponseRedirect(reverse("jobs:titles"))

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
def index__get_job_filter(session):
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
