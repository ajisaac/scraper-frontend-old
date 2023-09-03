from django.urls import path

from . import views

app_name = "jobs"
urlpatterns = [

    # the main jobs page                /
    path("", views.index, name="index"),

    # update status for any job         /update_status/5
    path("update_status/<int:job_id>", views.update_status, name="update_status"),

    # filter by status for main page    /status/new
    path("status/<str:status>", views.main__status_filter, name="status_filter"),
    path("main__filter_search", views.main__filter_search, name="main__filter_search"),

    # the main titles page              /titles
    path("titles", views.titles, name="titles"),
    path("titles_title_search", views.titles_title_search,
         name="titles_title_search"),
]
