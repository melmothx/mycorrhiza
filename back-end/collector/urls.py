from django.urls import path

from . import views

urlpatterns = [
    path("api", views.api, name="api"),
    path("api/merge/<target>", views.api_merge, name="api_merge"),
    path("api/exclusions", views.exclusions, name="exclusions"),
    path("spreadsheet", views.upload_spreadsheet, name="spreadsheet"),
    path("spreadsheet/<target>", views.process_spreadsheet, name="process_spreadsheet"),
]
