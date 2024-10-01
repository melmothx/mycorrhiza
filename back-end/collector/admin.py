from django.contrib import admin
from .models import Site, Harvest, Language, NameAlias, SpreadsheetUpload, Library, User, Page, General

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    exclude = ["last_harvested", "amusewiki_formats"]

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    exclude = [
        "password",
        "groups",
        "user_permissions",
        "last_login",
        "password_reset_token",
        "password_reset_expiration",
        "date_joined",
    ]

# Register your models here.
admin.site.register(Harvest)
admin.site.register(Language)
admin.site.register(NameAlias)
admin.site.register(SpreadsheetUpload)
admin.site.register(Library)
admin.site.register(Page)
admin.site.register(General)
