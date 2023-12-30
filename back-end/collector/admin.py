
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Site, Harvest, Agent, Subject, Entry, Language, NameAlias, Profile, SpreadsheetUpload

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "profiles"

class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register your models here.
admin.site.register(Site)
admin.site.register(Harvest)
admin.site.register(Agent)
admin.site.register(Subject)
admin.site.register(Entry)
admin.site.register(Language)
admin.site.register(NameAlias)
admin.site.register(SpreadsheetUpload)
