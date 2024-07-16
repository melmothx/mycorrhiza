# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, Http404
from django.template import loader
import json
from amwmeta.xapian import search
import logging
from django.urls import reverse
from django.conf import settings
from amwmeta.utils import paginator, page_list
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.password_validation import validate_password, password_validators_help_texts
from django.db.models import Q
from .models import Profile, Entry, Agent, Site, SpreadsheetUpload, DataSource, Library, Exclusion, AggregationEntry, ChangeLog, manipulate, log_user_operation
from django.contrib.auth.models import User
from amwmeta.xapian import MycorrhizaIndexer
from .forms import SpreadsheetForm
from django.contrib import messages
from django.contrib.syndication.views import Feed
from django.core.mail import send_mail
from secrets import token_urlsafe
from http import HTTPStatus
from urllib.parse import urlparse
from datetime import datetime, timedelta, timezone
import re
import requests
# from django.db import connection
import pprint
pp = pprint.PrettyPrinter(indent=2)


logger = logging.getLogger(__name__)

def user_is_library_admin(user):
    if not user.username:
        return False
    if user.is_superuser:
        return True
    elif hasattr(user, "profile") and user.profile.library_admin:
        return True
    else:
        return False


def api_login(request):
    out = { "logged_in": None, "error": None }
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        out['error'] = "Invalid JSON!";
    user = authenticate(request, username=data.get('username'), password=data.get('password'))
    if user is not None:
        login(request, user)
        out = _user_data(user)
    else:
        out['error'] = 'Invalid login'
    logger.debug(out)
    return JsonResponse(out)

def api_logout(request):
    logout(request)
    return JsonResponse({ "ok": "Logged out" })

def api_reset_password(request):
    out = {}
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        out['error'] = "Invalid JSON!";

    user = None
    try:
        user = User.objects.get(username=data.get('username'))
    except User.DoesNotExist:
        pass

    operation = data.get('operation')
    new_password = data.get('password')
    token = data.get('token')

    # logger.debug(pp.pformat(data))

    if user:
        # make sure to create the profile, if missing
        profile = None
        if hasattr(user, 'profile'):
            profile = user.profile
        else:
            profile = Profile.objects.create(user=user)

        if operation == 'send-link':
            if not profile.has_valid_password_reset():
                profile.password_reset_token = token_urlsafe(16)
                profile.password_reset_expiration = datetime.now(timezone.utc) + timedelta(minutes=10)
                profile.save()
                url = "{}/reset-password/{}/{}".format(settings.CANONICAL_ADDRESS,
                                                       user.username,
                                                       profile.password_reset_token)
                send_mail("Password reset for {} (account {})".format(settings.CANONICAL_ADDRESS, user.username),
                          "Please visit {} to reset your password. The link is valid for 10 minutes.".format(url),
                          settings.MYCORRHIZA_EMAIL_FROM,
                          [user.email])
                out['message'] = "We tried to send an email to this account. Please check your inbox."
            else:
                out['message'] = "We already sent an email few minutes ago. Please check again your inbox."

        elif operation == 'reset' and new_password and token:
            password_validation_errors = None
            try:
                validate_password(new_password, user=user)
            except ValidationError as error:
                password_validation_errors = " ".join(error)

            if not password_validation_errors:
                if profile.has_valid_password_reset() and token == profile.password_reset_token:
                    logger.info("Successful password reset for {}".format(user.username))
                    user.set_password(new_password)
                    user.save()
                    new_user = authenticate(request, username=user.username, password=new_password)
                    if new_user is not None:
                        login(request, new_user)
                        profile.password_reset_token = None
                        profile.password_reset_expiration = None
                        profile.save()
                        out['logged_in'] = user.username
                    else:
                        out['error'] = "We could not log you in, this is a bug"
                else:
                    out['error'] = "Invalid reset token"
            else:
                out['error'] = password_validation_errors
        else:
            out['error'] = "Invalid operation"
    else:
        out['error'] = "Invalid user"
    return JsonResponse(out)

@ensure_csrf_cookie
def api_user(request):
    return JsonResponse(_user_data(request.user))

def _user_data(user):
    out = {
        "logged_in": user.username,
        "is_superuser": user.is_superuser,
        "is_library_admin": False,
        "libraries": [],
    }
    if user.username and hasattr(user, "profile"):
        profile = user.profile
        out["is_library_admin"] = profile.library_admin
        out["libraries"] = [ { "id": l.id, "name": l.name } for l in profile.libraries.filter(active=True).all() ]

    return out

def _active_libraries(user):
    query = Q(active=True) & Q(public=True)
    if user.is_authenticated and user.is_superuser:
        # exclude only the inactive
        query = Q(active=True)
    elif user.is_authenticated:
        additional = Q(active=True) & Q(public=False) & Q(shared=True)
        query = query | additional
        if hasattr(user, "profile"):
            private = []
            for lib in user.profile.libraries.filter(active=True, public=False, shared=False).only('id').all():
                private.append(lib.id)
            if private:
                query = query | Q(id__in=private)
    logger.debug("Query is {}".format(query))
    active_libraries = [ lib.id for lib in Library.objects.filter(query).only('id').all() ]
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
    res['can_set_exclusions'] = user.is_superuser
    res['can_merge'] = user.is_superuser
    if user.is_authenticated and not user.is_superuser and hasattr(user, "profile"):
        res['can_merge'] = res['can_set_exclusions'] = user.profile.library_admin
    return JsonResponse(res)

class LatestEntriesFeed(Feed):
    title = 'Latest entries'
    link = "{}/feed".format(settings.CANONICAL_ADDRESS)
    feed_url = "{}/feed".format(settings.CANONICAL_ADDRESS)
    description = 'Latest entries sorted by acquisition date'
    def items(self):
        query = {
            "page_size": 50,
            "page_number": 1,
            "query": "",
            "sort_by": "datestamp",
            "sort_direction": "desc",
        }
        res = search(settings.XAPIAN_DB,
                     query,
                     active_libraries=[ lib.id for lib in Library.objects.filter(active=True, public=True).all() ],
                     matches_only=True)
        return res

    def item_title(self, item):
        title = ""
        try:
            title = item['title'][0]['value']
        except KeyError:
            pass
        except IndexError:
            pass
        return title

    def item_description(self, item):
        desc = ""
        try:
            desc = item['description'][0]['value']
        except KeyError:
            pass
        except IndexError:
            pass
        return desc

    def item_link(self, item):
        return "{}/entry/{}".format(settings.CANONICAL_ADDRESS, item['entry_id'])

def get_entry(request, entry_id):
    entry = get_object_or_404(Entry, pk=entry_id)
    record = entry.display_data(library_ids=_active_libraries(request.user))
    logger.debug(pp.pformat(record))
    return JsonResponse(record)

# should this be login required?
def get_datasource_full_text(request, ds_id):
    ds = get_object_or_404(DataSource, pk=ds_id)
    out = {}
    html = ""
    if ds.site.library_id in _active_libraries(request.user):
        html = ds.full_text()

    def replace_images(m):
        src = reverse('api_get_datasource_file', args=[ds.id, m.group(1)])
        return 'src="' + src + '"'

    if html:
        out['html'] = re.sub(r'src="([0-9a-z-]+\.(jpe?g|png))"', replace_images, html)
    return JsonResponse(out)

def get_datasource_file(request, ds_id, filename):
    ds = get_object_or_404(DataSource, pk=ds_id)
    if ds.site.library_id in _active_libraries(request.user):
        text_uri = ds.amusewiki_base_url()
        if text_uri:
            if re.match(r'^[a-z0-9-\.]+$', filename):
                file_uri = re.sub(r'/[a-z0-9-\.]+$', '/' + filename, text_uri)
                logger.debug("Proxying {}".format(file_uri))
                r = requests.get(file_uri)
                if r.status_code == 200:
                    return HttpResponse(r.content, content_type=r.headers['content-type'])
                else:
                    raise Http404("File not found!")
            else:
                raise Http404("Invalid argument!")
        else:
            raise Http404("Invalid file!")
    else:
        raise Http404("Not found")

def download_datasource(request, target):
    check = re.compile(r'(\d+)((\.[a-z0-9]+)+)$')
    m = check.match(target)
    if m:
        ds_id = m.group(1)
        ds = get_object_or_404(DataSource, pk=ds_id)
        ext = m.group(2)
        if ds.site.library_id in _active_libraries(request.user):
            r = ds.get_remote_file(ext)
            if r and r.status_code == 200:
                response = HttpResponse(r.content, content_type=r.headers['content-type'])
                target = urlparse(r.url)
                response.headers['Content-Disposition'] = 'attachment; filename="{}.{}"'.format(
                    target.hostname,
                    re.split(r'/', target.path)[-1]
                )
                return response
            else:
                raise Http404("File not found!")
        else:
            raise Http404("Not such DS")
    else:
        raise Http404("Not found")

@user_passes_test(user_is_library_admin)
def api_library_edit(request, library_id):
    out = {
        "error": None,
        "library": None,
        "users": [],
    }
    library = None
    user = request.user
    try:
        if user.is_superuser:
            library = Library.objects.get(pk=library_id)
        elif hasattr(user, 'profile'):
            library = user.profile.libraries.get(pk=library_id)
    except Library.DoesNotExist:
        out['error'] = "You cannot access this library"

    if library and request.method == 'POST':
        try:
            data = json.loads(request.body)
            # expecting all these keys:
            for f in ['name',
                      'url',
                      'email_public',
                      'email_internal',
                      'opening_hours',
                      'latitude',
                      'longitude',
                      ]:
                value = data[f]
                if not value:
                    if f in [ 'latitude', 'longitude']:
                        value = None
                setattr(library, f, value)
            library.save()
        except json.JSONDecodeError:
            out['error'] = "Invalid JSON!";

    # refetch the values
    if library:
        out['library'] = Library.objects.values().get(pk=library.id)
        users = []
        for profile in library.affiliated_profiles.filter(library_admin=False).all():
            user = profile.user
            users.append({
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "last_login": user.last_login,
            })
        out['users'] = users

    return JsonResponse(out)

@user_passes_test(user_is_library_admin)
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

@user_passes_test(user_is_library_admin)
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

@user_passes_test(user_is_library_admin)
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

@user_passes_test(user_is_library_admin)
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

@user_passes_test(user_is_library_admin)
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

@user_passes_test(user_is_library_admin)
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
    logger.debug(out)
    return JsonResponse(out)

@user_passes_test(user_is_library_admin)
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

@user_passes_test(user_is_library_admin)
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
