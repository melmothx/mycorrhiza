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
from .models import User, Entry, Agent, Site, SpreadsheetUpload, DataSource, Library, Exclusion, AggregationEntry, ChangeLog, manipulate, log_user_operation
from amwmeta.xapian import MycorrhizaIndexer
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
    elif user.library_admin:
        return True
    else:
        return False

def user_can_merge(user):
    if not user.username:
        return False
    if user.is_superuser:
        return True
    elif user.can_merge_entries():
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

        if operation == 'send-link':
            if not user.has_valid_password_reset():
                user.password_reset_token = token_urlsafe(16)
                user.password_reset_expiration = datetime.now(timezone.utc) + timedelta(minutes=10)
                user.save()
                url = "{}/reset-password/{}/{}".format(settings.CANONICAL_ADDRESS,
                                                       user.username,
                                                       user.password_reset_token)
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
                if user.has_valid_password_reset() and token == user.password_reset_token:
                    logger.info("Successful password reset for {}".format(user.username))
                    user.set_password(new_password)
                    user.save()
                    new_user = authenticate(request, username=user.username, password=new_password)
                    if new_user is not None:
                        login(request, new_user)
                        user.password_reset_token = None
                        user.password_reset_expiration = None
                        user.save()
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

@user_passes_test(user_is_library_admin)
def api_user_check(request, username):
    has_username = User.objects.filter(username=username.strip().lower()).count()
    return JsonResponse({ "username": username, "username_exists": has_username })

def _user_data(user):
    out = {
        "logged_in": None,
        "is_superuser": False,
        "is_library_admin": False,
        "libraries": [],
        "message": None,
    }
    if user and user.username:

        if user.expiration and datetime.now(timezone.utc) > user.expiration:
            logger.info("Removing {}: expired account on {}".format(user.username, user.expiration))
            user.delete()
            out["message"] = "Sorry, your account is expired!"
            return out
        out["logged_in"] = user.username
        out["is_superuser"] = user.is_superuser
        out["is_library_admin"] = user.library_admin
        out["libraries"] = [ { "id": l.id, "name": l.name } for l in user.libraries.filter(active=True).all() ]

    return out

def _active_libraries(user):
    # default: active and public
    query = Q(active=True) & Q(public=True)
    if user.is_authenticated:
        # admin: exclude only the inactive
        query = Q(active=True)
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

    if user.is_authenticated and not user.is_superuser:
        # authenticated users can set exclusion
        res['can_set_exclusions'] = True
        res['can_merge'] = user.can_merge_entries()

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
        except (KeyError, IndexError):
            pass
        return title

    def item_description(self, item):
        desc = ""
        try:
            desc = item['description'][0]['value']
        except (KeyError, IndexError):
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
        site = ds.site
        if site.library_id in _active_libraries(request.user):
            site_type = site.site_type
            if site_type == 'amusewiki':
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
            elif site_type == 'calibretree':
                f = ds.get_calibre_file(ext)
                if f:
                    content_types = {
                        ".pdf": "application/pdf",
                        ".epub": "application/epub+zip",
                        ".txt": "text/plain",
                    }
                    response = HttpResponse(f.read_bytes(), content_type=content_types[ext])
                    response.headers['Content-Disposition'] = 'attachment; filename="{}.{}"'.format(site.hostname(), f.name)
                    return response
                else:
                    raise Http404("File not found!")
            else:
                raise Http404("Not such DS")
        else:
            raise Http404("Not found")
    else:
        raise Http404("Not found")

@user_passes_test(user_is_library_admin)
def api_library_action(request, action, library_id):
    out = {
        "error": None,
        "library": None,
    }
    columns = [
        'url',
        'email_public',
        'email_internal',
        'opening_hours',
        'latitude',
        'longitude',
    ]
    library = None
    user = request.user
    try:
        if user.is_superuser:
            library = Library.objects.get(pk=library_id)
        elif user.username:
            library = user.libraries.get(pk=library_id)
    except Library.DoesNotExist:
        out['error'] = "You cannot access this library"

    if library and request.method == 'POST':
        try:
            data = json.loads(request.body)
            # expecting all these keys:
            if action == "details":
                for f in columns:
                    value = data[f]
                    if not value and f in [ 'latitude', 'longitude']:
                        value = None
                    setattr(library, f, value)
                library.save()
                out['success'] = 'OK'
            elif action == "remove-user":
                userid = data.get('id')
                if userid:
                    logger.debug("Removing {}".format(userid))
                    try:
                        affiliate = library.affiliated_users.get(pk=userid)
                        affiliate.libraries.remove(library)
                        # should we keep the user or set the user inactive?
                        if not affiliate.libraries.count():
                            logger.info("No other library associated, removing")
                            affiliate.delete();
                    except User.DoesNotExist:
                        out['error'] = "No such affiliated user"
            elif action == "create-user":
                logger.debug(pp.pformat(data))
                username = data.get('username', '').strip().lower()
                logger.debug("Creating {}".format(username))
                if username:
                    try:
                        affiliate = User.objects.get(username=username)
                    except User.DoesNotExist:
                        user_args = {
                            "first_name": data.get('first_name', '').strip(),
                            "last_name": data.get('last_name', '').strip(),
                            "password_reset_token": token_urlsafe(16),
                            "password_reset_expiration": datetime.now(timezone.utc) + timedelta(minutes=10),
                        }
                        if data.get('can_merge'):
                            user_args['can_merge'] = True
                        if data.get('expiration'):
                            user_args['expiration'] = data.get('expiration')

                        affiliate = User.objects.create_user(username,
                                                        data.get('email') or library.email_internal,
                                                        **user_args)
                        affiliate.refresh_from_db()
                        if affiliate.email:
                            url = "{}/reset-password/{}/{}".format(settings.CANONICAL_ADDRESS,
                                                                   affiliate.username,
                                                                   affiliate.password_reset_token)
                            mail_body = [
                                "Your user {} has been created.".format(affiliate.username),
                                "Please visit {} to set the password.".format(url),
                                "The link is valid for 10 minutes. You can always request another link one.",
                            ]
                            if affiliate.expiration:
                                iso_date = affiliate.expiration.strftime('%Y-%m-%d')
                                mail_body.append("This account will expire on {}.".format(iso_date))

                            send_mail("Password reset for {} (account {})".format(settings.CANONICAL_ADDRESS,
                                                                                  affiliate.username),
                                      "\n\n".join(mail_body),
                                      settings.MYCORRHIZA_EMAIL_FROM,
                                      [affiliate.email])

                    if affiliate.libraries.filter(pk=library.id).count():
                        logger.info("User already has the library")
                        out['error'] = "User already present"
                    else:
                        logger.info("Adding {} to {}".format(affiliate.username, library.name))
                        affiliate.libraries.add(library)
                        out['success'] = "User added"

        except json.JSONDecodeError:
            out['error'] = "Invalid JSON!";

    # refetch the values
    if library:
        if action == 'details':
            out['library'] = Library.objects.values().get(pk=library.id)
        elif action == 'list-users':
            users = []
            for affl in library.affiliated_users.filter(library_admin=False).all():
                user_data = {
                    "id": affl.id,
                    "username": affl.username,
                    "email": affl.email,
                    "name": "{} {}".format(affl.first_name, affl.last_name),
                    "last_login": None,
                    "can_merge": None,
                    "expiration": None,
                }
                if affl.can_merge:
                    user_data["can_merge"] = "Yes"
                if affl.expiration:
                    user_data["expiration"] = affl.expiration.strftime('%Y-%m-%d')

                if affl.last_login:
                    user_data['last_login'] = affl.last_login.strftime('%Y-%m-%d')
                users.append(user_data)

            out['records'] = users
            out['fields'] = [
                { 'name': 'id', 'label': 'Id' },
                { 'name': 'username', 'label': 'Username' },
                { 'name': 'email', 'label': 'Email' },
                { 'name': 'name', 'label': 'Name' },
                { 'name': 'last_login', 'label': 'Last Login' },
                { 'name': 'expiration', 'label': 'Expires' },
                { 'name': 'can_merge', 'label': 'Can Merge' },

            ]
    return JsonResponse(out)

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

@user_passes_test(user_can_merge)
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

@user_passes_test(user_can_merge)
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

@user_passes_test(user_can_merge)
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
    if target == 'merged-agents' and user_can_merge(request.user):
        merged = []
        for agent in Agent.objects.filter(canonical_agent_id__isnull=False).all():
            apidata = agent.as_api_dict(get_canonical=True)
            if apidata.get('canonical'):
                for f in ['id', 'name']:
                    apidata['canonical_' + f] = apidata['canonical'][f]
                merged.append(apidata)
        out['records'] = merged
        out['fields'] = [
            { 'name': 'id', 'label': 'Id' },
            { 'name': 'name', 'label': 'Name' },
            { 'name': 'canonical_id', 'label': 'Canonical ID' },
            { 'name': 'canonical_name', 'label': 'Canonical Name' },
        ]

    elif target == 'translations' and user_can_merge(request.user):
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


    elif target == 'merged-entries' and user_can_merge(request.user):
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
        for ex in Exclusion.objects.filter(user=request.user).all():
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
    logger.debug(out)
    return JsonResponse(out)

@user_passes_test(user_is_library_admin)
def api_spreadsheet(request, library_id):
    out = {
        "sites": [],
    }
    library = None
    sites = []
    user = request.user
    try:
        library = Library.objects.get(pk=library_id)
    except Library.DoesNotExist:
        out['error'] = "Library does not exist"
    if library:
        if user.is_superuser or library.affiliated_users.filter(library_admin=True, user=user).count():
            sites = [ { "title": s.title, "id": s.id } for s in library.sites.filter(site_type="csv", active=True) ]
    if sites:
        if request.method == 'POST':
            site_id = request.POST.get('site_id')
            logger.debug("Site id {}".format(site_id))
            logger.debug(pp.pformat(out))
            logger.debug(pp.pformat(request.FILES))
            logger.debug(pp.pformat(request.POST))
            if site_id and site_id in [ str(s['id']) for s in sites ]:
                replace_all = False
                if request.POST.get('replace_all', False):
                    replace_all = True
                logger.debug("Creating spreadsheet upload")
                ss = SpreadsheetUpload.objects.create(user=user,
                                                      spreadsheet=request.FILES['spreadsheet'],
                                                      comment=request.POST.get('comment', ''),
                                                      site_id=site_id,
                                                      replace_all=replace_all)
                validation = ss.validate_csv()
                logger.debug(validation)
                validated_sample = validation['sample']
                out['sample'] = [ { "name": k, "value":  validated_sample[k] } for k in validated_sample ]
                out['error'] = validation['error']
                if not validation['error']:
                    out['uploaded'] = ss.id
                    out['success'] = "Spreadsheet uploaded"
                else:
                    # remove record?
                    pass
            else:
                out['error'] = "Invalid parameters"
        else:
            out['sites'] = sites

    return JsonResponse(out)

@user_passes_test(user_is_library_admin)
def api_process_spreadsheet(request, spreadsheet_id):
    user = request.user
    out = {}
    ss = None
    try:
        ss = user.uploaded_spreadsheets.filter(processed=None).get(pk=spreadsheet_id)
    except SpreadsheetUpload.DoesNotExist:
        out['error'] = "Bad ID"

    if request.method == "POST" and ss:
        if ss.validate_csv()['sample']:
            ss.process_csv()
            out['success'] = "Sheet processed"
        else:
            out['error'] = "Invalid CSV"

    return JsonResponse(out)

