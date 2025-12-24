from django.contrib import admin
from .models import Site, Language, NameAlias, SpreadsheetUpload, Library, User, Page, General, ChangeLog, InternalLibraryCode

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    exclude = ["last_harvested", "amusewiki_formats"]
    search_fields = ['title', 'url', 'comment', 'library__name', 'library__url']

@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    search_fields = ['name', 'url', 'description', 'email_public', 'email_internal']


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
    search_fields = ['email', 'username', 'first_name', 'last_name']

# Register your models here.
admin.site.register(Language)
admin.site.register(NameAlias)
admin.site.register(SpreadsheetUpload)
admin.site.register(Page)
admin.site.register(General)
admin.site.register(ChangeLog)
admin.site.register(InternalLibraryCode)
