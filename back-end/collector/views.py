# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, Http404
from django.template import loader
import json
from amwmeta.xapian import search
import logging
from django.urls import reverse
from amwmeta.utils import paginator, page_list
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Entry, Agent, Site, SpreadsheetUpload, DataSource, Library
from amwmeta.xapian import MycorrhizaIndexer
from .forms import SpreadsheetForm
from django.contrib import messages
from http import HTTPStatus
import re

logger = logging.getLogger(__name__)

def api_login(request):
    out = { "logged_in": None, "error": None }
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        out['error'] = "Invalid JSON!";
    user = authenticate(request, username=data.get('username'), password=data.get('password'))
    if user is not None:
        login(request, user)
        out['logged_in'] = user.get_username()
    else:
        out['error'] = 'Invalid login'
    logger.debug(out)
    return JsonResponse(out)

def api_logout(request):
    logout(request)
    return JsonResponse({ "ok": "Logged out" })

def api_user(request):
    # guaranteed to return the empty string
    return JsonResponse({ "logged_in": request.user.get_username() })

def _active_libraries(user):
    active_libraries = [ lib.id for lib in Library.objects.filter(active=True, public=True).all() ]
    if user.is_authenticated and user.is_superuser:
        # exclude only the inactive
        active_libraries = [ lib.id for lib in Library.objects.filter(active=True).all() ]
    elif user.is_authenticated and user.profile:
        # add the private one from the profile
        active_libraries.extend([ lib.id for lib in user.profile.libraries.filter(active=True, public=False).all() ])
    logger.debug("Active libs are {}".format(active_libraries))
    return active_libraries

def api(request):
    public_only = True

    user = request.user
    active_libraries = _active_libraries(user)
    logger.debug("User libraries: {}".format(active_libraries))

    exclusions = []
    can_set_exclusions = False
    if user.is_authenticated:
        exclusions = []
        for exclusion in user.exclusions.all():
            exclusions.extend(exclusion.as_xapian_queries())
        logger.debug("Exclusions: {}".format(exclusions))
        can_set_exclusions = True

    res = search(
        request.GET,
        active_libraries=active_libraries,
        exclusions=exclusions,
    )
    res['total_entries'] = res['pager'].total_entries
    res['pager'] = page_list(res['pager'])
    res['is_authenticated'] = user.is_authenticated
    res['can_set_exclusions'] = can_set_exclusions
    return JsonResponse(res)

def get_entry(request, entry_id):
    entry = get_object_or_404(Entry, pk=entry_id)
    record = entry.display_data(library_ids=_active_libraries(request.user))
    if not record['data_sources']:
        raise Http404("No data sources!")
    return JsonResponse(record)

# should this be login required?
def get_datasource_full_text(request, ds_id):
    ds = get_object_or_404(DataSource, pk=ds_id)
    out = {}
    if ds.site.library_id in _active_libraries(request.user):
        out['html'] = ds.full_text()
    logger.debug(out)
    return JsonResponse(out)

def download_datasource(request, target):
    check = re.compile(r'(\d+)((\.[a-z0-9]+)+)$')
    m = check.match(target)
    if m:
        ds_id = m.group(1)
        ds = get_object_or_404(DataSource, pk=ds_id)
        ext = m.group(2)
        if ds.site.library_id in _active_libraries(request.user):
            r = ds.get_remote_file(ext)
            if r.status_code == 200:
                response = HttpResponse(r.content, content_type=r.headers['content-type'])
                response.headers['Content-Disposition'] = 'attachment; filename="{}"'.format(re.split(r'/', r.url)[-1])
                return response
            else:
                raise Http404("File not found!")
        else:
            raise Http404("Not such DS")
    else:
        raise Http404("Not found")

@login_required
def exclusions(request):
    logger.debug(request.body)
    out = {}
    data = None
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        out['error'] = "Invalid JSON!";

    if data:
        logger.debug(data)
        user = request.user
        op = data.get('op')
        what = data.get('type')
        object_id = data.get('id')
        comment = data.get('comment')
        if op and what and object_id:
            if op == 'add' and comment:
                if what in [ 'author', 'entry', 'library' ]:
                    creation = {
                        "comment": comment,
                        "exclude_{}_id".format(what): object_id,
                        "user": user,
                    }
                    logger.debug(creation)
                    exclusion = user.exclusions.create(**creation)
                    out['success'] = exclusion.id

            elif op == 'remove':
                pass
            elif op == 'list':
                pass
            else:
                out['error'] = "Invalid operation {}".format(op)
        else:
            out['error'] = "Missing parameters"
    logger.debug(out)
    return JsonResponse(out)

@login_required
def api_set_translations(request):
    out = {}
    data = None
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        out['error'] = "Invalid JSON!";

    if data:
        logger.debug(data)
        # reindex all
        reindex = [  x['id'] for x in data ]
        original = Entry.objects.get(pk=data.pop(0)['id'])
        original.original_entry = None
        original.save()
        translations = [ x['id'] for x in data ]
        Entry.objects.filter(id__in=[ x['id'] for x in data ]).update(original_entry=original)
        indexer = MycorrhizaIndexer()
        indexer.index_entries(Entry.objects.filter(id__in=reindex).all())
        out['success'] = "Translations set!"

    logger.debug(out)
    return JsonResponse(out)

@login_required
def api_merge(request, target):
    logger.debug(target)
    out = {}
    data = None
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        out['error'] = "Invalid JSON!";

    if data:
        logger.debug(data)
        canonical = None
        aliases = []
        classes = {
            "entry" : Entry,
            "author" : Agent,
        }
        if target in classes:
            current_class = classes[target]
            for pk in [ x['id'] for x in data ]:
                try:
                    obj = current_class.objects.get(pk=pk)
                    if canonical:
                        aliases.append(obj)
                    else:
                        canonical = obj
                except current_class.DoesNotExist:
                    logger.debug("Invalid entry " + pk)

            if canonical and aliases:
                if canonical.id not in [ x.id for x in aliases ]:
                    logger.info("Merging " + str(aliases) + " into " + str(canonical))
                    reindex = current_class.merge_records(canonical, aliases)
                    indexer = MycorrhizaIndexer()
                    indexer.index_entries(reindex)
                    logger.info(indexer.logs)
                    out['success'] = "Merged!"
                else:
                    out['error'] = "You can't merge an item with itself!"
            else:
                out['error'] = "Bad arguments! Expecting valid canonical and a list of aliases!"
        else:
            out['error'] = 'Invalid path'
    logger.debug(out)
    return JsonResponse(out)

@login_required
def upload_spreadsheet(request):
    user = request.user
    if user.is_superuser:
        queryset = Site.objects.filter(active=True, site_types="csv").order_by("url")
    else:
        active_libraries = _active_libraries(user)
        queryset = Site.objects.filter(library_id__in=active_libraries,
                                       active=True,
                                       site_types="csv").order_by("url")

    form = SpreadsheetForm()
    if request.method == "POST":
        form = SpreadsheetForm(request.POST, request.FILES)

    form.fields["site"].queryset = queryset

    if request.method == "POST" and form.is_valid():
        logger.debug("Form is valid")
        new_sheet = form.save()
        new_sheet.user = user
        new_sheet.save()
        return HttpResponseRedirect(reverse("process_spreadsheet", args=[new_sheet.id]))

    return render(request, "collector/spreadsheet.html", { "form": form })

@login_required
def process_spreadsheet(request, target):
    sheet = get_object_or_404(SpreadsheetUpload, pk=target)
    if sheet and sheet.user and sheet.user.id == request.user.id:
        sample = sheet.validate_csv()
        if sample:
            if request.method == "POST" and request.POST and request.POST["process"]:
                sheet.process_csv()
                messages.success(request, "Spreadsheet Processed")
                return HttpResponseRedirect(reverse("spreadsheet"))
            else:
                return render(
                    request,
                    "collector/process_spreadsheet.html",
                    {
                        "target": target,
                        "sample": sample,
                    }
                )
        else:
            messages.error(request, "Invalid CSV")
            return HttpResponseRedirect(reverse("spreadsheet"))
    else:
        raise Http404("You did not upload such sheet")
