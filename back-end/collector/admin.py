
from django.contrib import admin

from .models import Site, Harvest, Agent, Subject, Entry, Language, NameAlias

# Register your models here.
admin.site.register(Site)
admin.site.register(Harvest)
admin.site.register(Agent)
admin.site.register(Subject)
admin.site.register(Entry)
admin.site.register(Language)
admin.site.register(NameAlias)
