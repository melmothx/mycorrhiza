from django.urls import path

from . import views

urlpatterns = [
    path("api", views.api, name="api"),
    path("api/auth/login", views.api_login, name="api_login"),
    path("api/auth/logout", views.api_logout, name="api_logout"),
    path("api/auth/user", views.api_user, name="api_user"),
    path("api/entry/<entry_id>", views.get_entry, name="api_get_entry"),
    path("api/full-text/<ds_id>", views.get_datasource_full_text, name="api_full_text"),
    path("api/merge/<target>", views.api_merge, name="api_merge"),
    path("api/set-translations", views.api_set_translations, name="api_set_translations"),
    path("api/exclusions", views.exclusions, name="exclusions"),
    path("spreadsheet", views.upload_spreadsheet, name="spreadsheet"),
    path("spreadsheet/<target>", views.process_spreadsheet, name="process_spreadsheet"),
]
