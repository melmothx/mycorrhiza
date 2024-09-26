from django.urls import path

from . import views

urlpatterns = [
    path("api/search", views.api_search, name="api_search"),
    path("api/auth/login", views.api_login, name="api_login"),
    path("api/auth/logout", views.api_logout, name="api_logout"),
    path("api/auth/reset-password", views.api_reset_password, name="api_reset_password"),
    path("api/auth/user", views.api_user, name="api_user"),
    path("api/auth/user-check/<username>", views.api_user_check, name="api_user_check"),
    path("api/entry/<int:entry_id>", views.get_entry, name="api_get_entry"),
    path("api/full-text/<int:ds_id>", views.get_datasource_full_text, name="api_full_text"),
    path("api/file/<int:ds_id>/<filename>", views.get_datasource_file, name="api_get_datasource_file"),
    path("api/download/<target>", views.download_datasource, name="api_download_datasource"),
    path("api/merge/<target>", views.api_merge, name="api_merge"),
    path("api/listing/<target>", views.api_listing, name="api_listing"),
    path("api/revert/<target>", views.api_revert, name="api_revert"),
    path("api/set-translations", views.api_set_translations, name="api_set_translations"),
    path("api/set-aggregated", views.api_set_aggregated, name="api_set_aggregated"),
    path("api/exclusions", views.exclusions, name="exclusions"),
    path("api/create/<target>", views.api_create, name="api_create"),
    path("api/library/<action>/<int:library_id>", views.api_library_action, name="api_library_action"),

    path("api/libraries", views.api_list_libraries, name="api_list_libraries"),
    path("api/libraries/<int:library_id>", views.api_show_library, name="api_show_library"),
    path("api/agents", views.api_list_agents, name="api_list_agents"),
    path("api/agents/<int:agent_id>", views.api_agent, name="api_agent"),

    path("api/spreadsheet/<int:library_id>", views.api_spreadsheet, name="api_spreadsheet"),
    path("api/spreadsheet/process/<int:spreadsheet_id>", views.api_process_spreadsheet, name="api_process_spreadsheet"),
]
