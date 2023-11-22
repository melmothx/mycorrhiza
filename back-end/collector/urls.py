from django.urls import path

from . import views

urlpatterns = [
    path("api", views.api, name="api"),
    path("api/merge/<target>", views.api_merge, name="api_merge"),
]
