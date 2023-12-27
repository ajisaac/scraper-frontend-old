from functools import reduce
import json
import operator
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q

from app.models import Job


#########################################################################################################
################################################ MAIN PAGE ##############################################
#########################################################################################################


def index__populate_session(request):
    '''
    populates the session if it doesn't exist
    '''
    session = request.session
    session['index__company_search'] = session.get('index__company_search', "")
    session['index__title_search'] = session.get('index__title_search', "")
    session['index__text_search'] = session.get('index__text_search', "")
    session['index__status_filter'] = session.get('index__status_filter', "new")
    session['index__job_site_filter'] = session.get('index__job_site_filter', "all")


def index(request):
    """
    Filter jobs by company, title, and text, return main page
    """
    index__populate_session(request)
    session = request.session

    # FIND SEARCH TERMS
    companies = [company.strip().lower()
                 for company in session['index__company_search'].split(",")]

    titles = [title.strip().lower()
              for title in session['index__title_search'].split(",")]

    texts = [text.strip().lower()
             for text in session['index__text_search'].split(",")]

    status = session['index__status_filter']

    job_site = session['index__job_site_filter']

    # CREATE QUERIES
    comp_searches = reduce(
        operator.or_, (Q(company__icontains=company) for company in companies))
    text_searches = reduce(
        operator.or_, (Q(description__icontains=text) for text in texts))
    title_searches = reduce(
        operator.or_, (Q(title__icontains=title) for title in titles))

    # DO FILTERING
    jobs = Job.objects.filter(status=status)

    if job_site != "all":
        jobs = jobs.filter(job_site=job_site)

    # conditional filtering here
    if companies != [""]:
        jobs = jobs.filter(comp_searches)
    if texts != [""]:
        jobs = jobs.filter(text_searches)
    if titles != [""]:
        jobs = jobs.filter(title_searches)

    jobs_final = jobs.order_by("company", "title")

    jobs = jobs_final[:10]

    job_count = jobs_final.count()

    # query for all jobs by this company
    for job in jobs:
        if job.company is None:
            job.company_statuses = {}
        else:
            company_jobs = Job.objects.filter(company=job.company)
            company_jobs.distinct(status)
            job.company_statuses = {job.status for job in company_jobs}

    context = {"jobs": jobs,
               "job_count": job_count,
               "filter": filter}

    return HttpResponse(render(request, "jobs/index.html", context))


# when the user filters all jobs by status from main page
def index__status_filter(request, status):
    if not valid_status(status if not None else "new"):
        return HttpResponseRedirect(reverse("jobs:index"))

    request.session['index__status_filter'] = status
    return HttpResponseRedirect(reverse("jobs:index"))


# apply an exclusive filter for job site
def index__job_site_filter(request, job_site):
    request.session['index__job_site_filter'] = job_site
    return HttpResponseRedirect(reverse("jobs:index"))


def index__filter_search(request):
    request.session['index__company_search'] = request.POST[
        "index__company_search"] if "index__company_search" in request.POST else ""
    request.session['index__title_search'] = request.POST[
        "index__title_search"] if "index__title_search" in request.POST else ""
    request.session['index__text_search'] = request.POST[
        "index__text_search"] if "index__text_search" in request.POST else ""
    return HttpResponseRedirect(reverse("jobs:index"))


#########################################################################################################
################################################ TITLES PAGE ############################################
#########################################################################################################


def titles__populate_session(request):
    """
    populates the session if it doesn't exist
    """
    session = request.session
    session['titles__title_search'] = session.get('titles__title_search', "")


# the titles page
def titles(request):
    titles__populate_session(request)
    title_search: str = request.session['titles__title_search']

    jobs = Job.objects.order_by("title").filter(status="new")

    if title_search != "":
        jobs = jobs.filter(title__icontains=title_search)

    jobs = jobs.exclude(job_site='hacker_news')

    context = {"jobs": jobs,
               "jobs_size": jobs.count()}

    return HttpResponse(render(request, "jobs/titles.html", context))


def titles_title_search(request):
    request.session['titles__title_search'] = request.POST.get(
        'titles__title_search', "")
    return HttpResponseRedirect(reverse("jobs:titles"))


#########################################################################################################
################################################ REST ###################################################
#########################################################################################################

# REST API for updating job status
def rest__update_status(request, job_id):
    body = json.loads(request.body)
    status = body["status"]

    if not valid_status(status):
        return HttpResponse("Invalid status: " + status, status=400)

    job = get_object_or_404(Job, pk=job_id)
    job.status = status
    job.save()
    return HttpResponse(status=200)


#########################################################################################################
################################################ COMMON #################################################
#########################################################################################################

# update status of a single job from any page
def update_status(request, job_id):
    status = request.POST["status"]
    nex = request.POST["next"]

    if not valid_status(status):
        return HttpResponseRedirect(reverse(nex))

    job = get_object_or_404(Job, pk=job_id)
    job.status = status
    job.save()
    return HttpResponseRedirect(reverse(nex))


# the only set of valid statuses
def valid_status(status):
    return status in ["new", "declined", "interested", "later", "applied", "interviewing", "offer", "rejected"]
