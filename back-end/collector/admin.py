from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Site, Harvest, Agent, Subject, Entry, Language, NameAlias, Profile, SpreadsheetUpload, Library

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "profiles"

class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    exclude = ["last_harvested", "amusewiki_formats"]


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# Register your models here.
admin.site.register(Harvest)
admin.site.register(Language)
admin.site.register(NameAlias)
admin.site.register(SpreadsheetUpload)
admin.site.register(Library)
