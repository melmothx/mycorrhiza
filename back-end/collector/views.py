# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, Http404
from django.template import loader
import json
from amwmeta.xapian import search
import logging
from django.urls import reverse
from django.conf import settings
from amwmeta.utils import paginator, page_list
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Entry, Agent, Site, SpreadsheetUpload, DataSource, Library, Exclusion, AggregationEntry, ChangeLog, manipulate, log_user_operation
from amwmeta.xapian import MycorrhizaIndexer
from .forms import SpreadsheetForm
from django.contrib import messages
from http import HTTPStatus
import re
# from django.db import connection
import pprint
pp = pprint.PrettyPrinter(indent=2)


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
        settings.XAPIAN_DB,
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
    logger.debug(pp.pformat(record))
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
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            out['error'] = "Invalid JSON!";

    if request.method == 'GET':
        out['exclusions'] = [ i.as_api_dict() for i in request.user.exclusions.all() ]

    if data:
        logger.debug(data)
        user = request.user
        op = data.get('op')
        what = data.get('type')
        object_id = data.get('id')
        comment = data.get('comment')
        if op and object_id:
            if op == 'add' and comment and what:
                if what in [ 'author', 'entry', 'library' ]:
                    creation = {
                        "comment": comment,
                        "exclude_{}_id".format(what): object_id,
                        "user": user,
                    }
                    out = manipulate('add-exclusion', user, None, create=creation)
            elif op == 'delete':
                out = manipulate('revert-exclusion', user, object_id)
            else:
                out['error'] = "Invalid operation {}".format(op)
        else:
            out['error'] = "Missing parameters"
    logger.debug(out)
    return JsonResponse(out)

@login_required
def api_set_aggregated(request):
    out = {}
    data = None
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        out['error'] = "Invalid JSON!";
    user = request.user

    if data and user:
        ids = [ x['id'] for x in data ]
        out = manipulate('add-aggregations', user, *ids)
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
    user = request.user

    if data and user:
        logger.debug(data)
        ids = [ x['id'] for x in data ]
        out = manipulate('add-translations', user, *ids)
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

    user = request.user

    if data and user:
        logger.debug(data)
        method = {
            "entry" : "merge-entries",
            "author" : "merge-agents",
        }
        ids = [ x['id'] for x in data ]
        out = manipulate(method.get(target, 'invalid-method'), user, *ids)
    logger.debug(out)
    return JsonResponse(out)

@login_required
def api_create(request, target):
    logger.debug(target)
    out = {}
    data = None
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        out['error'] = "Invalid JSON!";

    user = request.user
    if data and user:
        logger.debug(data)
        created = None
        value = data.get('value')
        if value:
            if target == 'agent':
                # name is unique
                created, is_creation  = Agent.objects.get_or_create(name=value)
            elif target == 'aggregation':
                created = Entry.create_virtual_aggregation(value)

        if created:
            log_user_operation(user, 'create-' + target, created, None)
            out['created'] = {
                "id": created.id,
                "value": created.display_name(),
                "type": target,
            }
        else:
            out['error'] = "Invalid target (must be agent or aggregation)"

    logger.debug(out)
    return JsonResponse(out)

@login_required
def api_listing(request, target):
    out = {
        "target": target
    }
    if target == 'merged-agents':
        merged = []
        for agent in Agent.objects.filter(canonical_agent_id__isnull=False).all():
            apidata = agent.as_api_dict(get_canonical=True)
            if apidata.get('canonical'):
                for f in ['id', 'name']:
                    apidata['canonical_' + f] = apidata['canonical'][f]
                merged.append(apidata)
        out['records'] = merged
        out['fields'] = [
            { 'name': 'id', 'label': 'ID' },
            { 'name': 'name', 'label': 'Name' },
            { 'name': 'canonical_id', 'label': 'Canonical ID' },
            { 'name': 'canonical_name', 'label': 'Canonical Name' },
        ]

    elif target == 'translations':
        translations = []
        for entry in Entry.objects.filter(original_entry_id__isnull=False).all():
            apidata = entry.as_api_dict(get_original=True)
            if apidata.get('original'):
                # flatten for the table
                apidata['authors'] = '; '.join(apidata['authors'])
                apidata['languages'] = ' '.join(apidata['languages'])
                apidata['original_authors'] = '; '.join(apidata['original']['authors'])
                apidata['original_languages'] = ' '.join(apidata['original']['languages'])
                for f in ['id', 'title', 'created', 'last_modified', 'original']:
                    apidata['original_' + f] = apidata['original'][f]
                translations.append(apidata)

            else:
                logger.debug("Got an entry without a original? " + pp.pformat(apidata))

        out['fields'] = [
            { 'name': 'id', 'label': 'ID', 'link': 'entry' },
            { 'name': 'authors', 'label': 'Authors' },
            { 'name': 'title', 'label': 'Title' },
            { 'name': 'original_id', 'label': 'Original ID', 'link': 'entry' },
            { 'name': 'original_authors', 'label': 'Original Authors' },
            { 'name': 'original_title', 'label': 'Original Title' },
        ]
        out['records'] = translations


    elif target == 'merged-entries':
        merged = []
        for entry in Entry.objects.filter(canonical_entry_id__isnull=False).all():
            apidata = entry.as_api_dict(get_canonical=True)
            if apidata.get('canonical'):
                # flatten for the table
                apidata['authors'] = '; '.join(apidata['authors'])
                apidata['languages'] = ' '.join(apidata['languages'])
                apidata['canonical_authors'] = '; '.join(apidata['canonical']['authors'])
                apidata['canonical_languages'] = ' '.join(apidata['canonical']['languages'])
                for f in ['id', 'title', 'created', 'last_modified', 'canonical']:
                    apidata['canonical_' + f] = apidata['canonical'][f]
                merged.append(apidata)

            else:
                logger.debug("Got an entry without a canonical? " + pp.pformat(apidata))

        out['fields'] = [
            { 'name': 'id', 'label': 'ID', 'link': 'entry' },
            { 'name': 'authors', 'label': 'Authors' },
            { 'name': 'title', 'label': 'Title' },
            { 'name': 'canonical_id', 'label': 'Canonical ID', 'link': 'entry' },
            { 'name': 'canonical_authors', 'label': 'Canonical Authors' },
            { 'name': 'canonical_title', 'label': 'Canonical Title' },
        ]
        out['records'] = merged

    elif target == 'exclusions':
        records = []
        for ex in Exclusion.objects.all():
            rec = ex.as_api_dict()
            rec['username'] = rec['excluded_by']['username']
            records.append(rec)

        out['records'] = records
        out['fields'] = [
            { 'name': 'id', 'label': 'ID' },
            { 'name': 'username', 'label': 'Username'},
            { 'name': 'type', 'label': 'Type' },
            { 'name': 'target', 'label': 'Name' },
            { 'name': 'comment', 'label': 'Reason' },
        ]
    return JsonResponse(out)

@login_required
def api_revert(request, target):
    logger.debug(target)
    out = {}
    data = None
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        out['error'] = "Invalid JSON!";

    logger.debug(data)
    reindex = []
    user = request.user
    if data and user:
        object_id = data.get('id')
        if object_id:
            out = manipulate("revert-" + target, user, object_id)
        else:
            out['error'] = "Missing target ID"
    else:
        out['error'] = "Invalid data"
    return JsonResponse(out)

@login_required
def upload_spreadsheet(request):
    user = request.user
    if user.is_superuser:
        queryset = Site.objects.filter(active=True, site_type="csv").order_by("url")
    else:
        active_libraries = _active_libraries(user)
        queryset = Site.objects.filter(library_id__in=active_libraries,
                                       active=True,
                                       site_type="csv").order_by("url")

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
