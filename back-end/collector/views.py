# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, Http404, QueryDict
from django.template import loader
import json
from amwmeta.xapian import search
import logging
from django.urls import reverse
from django.conf import settings
from amwmeta.utils import paginator, page_list, log_user_operation
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.password_validation import validate_password, password_validators_help_texts
from django.db.models import Q
from .models import User, Entry, Agent, Site, SpreadsheetUpload, DataSource, Library, Exclusion, AggregationEntry, ChangeLog, Page, General, LibraryErrorReport
from .tasks import process_spreadsheet_upload, xapian_index_records
from django.contrib import messages
from django.contrib.syndication.views import Feed
from django.core.mail import send_mail, EmailMessage
from secrets import token_urlsafe
from http import HTTPStatus
from urllib.parse import urlparse
from datetime import datetime, timedelta, timezone
import re
from pathlib import Path
import requests
# from django.db import connection
import pprint
pp = pprint.PrettyPrinter(indent=2)

logger = logging.getLogger(__name__)

def manipulate(op, user, main_id, *ids, create=None):
    out = {
        "op": op,
        "main_id": main_id,
        "other_ids": ids,
        "error": None,
        "msg": None,
    }
    if not user:
        out['error']: "Missing User"
        return out

    out['username'] = user.username

    if op == "revert-exclusions" or op == "add-exclusion":
        # we just need the login
        pass
    elif user.is_superuser:
        pass
    elif user.can_merge_entries():
        # needs the can_merge_entries logic
        pass
    else:
        out['error'] = "Cannot do that"
        return out

    logger.info("Calling manipulate " + pp.pformat(out))
    reindex = []
    classes = {
        'merge-agents': Agent,
        'revert-merged-agents': Agent,

        'add-translations': Entry,
        'revert-translations': Entry,

        'merge-entries': Entry,
        'revert-merged-entries': Entry,

        'add-exclusion': Exclusion,
        'revert-exclusions': Exclusion,

        'add-aggregations': Entry,
        # no revert at the moment

    }
    if not main_id and not create:
        out['error']: "Missing ID"
        return out
    if not op:
        out['error']: "Missing operation"
        return out

    cls = classes.get(op)
    if not cls:
        out['error']: "Invalid operation"
        return out

    if main_id and main_id in ids:
        out['error']: "Recursive merging"
        return out

    if main_id:
        try:
            main_object = cls.objects.get(pk=main_id)
        except cls.DoesNotExist:
            out['error'] = "{} does not exist".format(main_id)
            return out
    elif create:
        # TODO: need to catch the exceptions
        main_object = cls.objects.create(**create)
        log_user_operation(user, op, main_object, None)
        out['success'] = "{} created".format(main_object.display_name())
        return out

    other_objects = []
    for oid in ids:
        try:
            obj = cls.objects.get(pk=oid)
            other_objects.append(obj)
        except cls.DoesNotExist:
            out['error'] = "{} does not exist".format(oid)
            return out

    reindex = []
    if op == 'merge-agents' or op == 'merge-entries':
        reindex = cls.merge_records(main_object, other_objects, user=user)
        out['success'] = "Merged"

    elif op == 'add-aggregations':
        if main_object.is_aggregation:
            reindex = cls.aggregate_entries(main_object, other_objects, user=user)
            if reindex:
                out['success'] = "Added"
        else:
            out['error'] = "First item must be an aggregation"

    elif op == 'revert-merged-agents' or op == 'revert-merged-entries':
        reindex = main_object.unmerge(user=user)
        if reindex:
            out['success'] = "Removed merge"
        else:
            out['error'] = "Nothing to do"

    elif op == 'add-translations':
        reindex = cls.translate_records(main_object, other_objects, user=user)
        if reindex:
            out['success'] = "Translations set!"
        else:
            out['error'] = "Nothing to do"

    elif op == 'revert-translations':
        reindex = main_object.untranslate(user=user)
        if reindex:
            out['success'] = "Removed translations"
        else:
            out['error'] = "Nothing to do"

    elif op == 'add-exclusion':
        raise Exception('Not reached')

    elif op == 'revert-exclusions':
        if main_object.user.username == user.username:
            log_user_operation(user, op, main_object, None)
            main_object.delete()
            out['success'] = "Removed"
        else:
            out['error'] = "Cannot do that"

    else:
        raise Exception("Bug! Missing handler for " + op)
    if reindex:
        xapian_index_records.delay_on_commit([ e.id for e in reindex ])
    return out

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
        out["email"] = user.email
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

def api_search(request):
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

    # use the facets from the base query
    base_query = QueryDict.fromkeys(["query"], value=res['querystring'])
    facets = search(
        settings.XAPIAN_DB,
        base_query,
        active_libraries=active_libraries,
        exclusions=exclusions,
        facets_only=True,
    )
    # mark the facets as active
    # logger.debug('Filters:' + pp.pformat(res['filters']))
    library_dict = { f['id']: f['name'] for f in Library.objects.values('id', 'name').all() }

    # if we have active filters, make sure they are listed as facets, even if the base query
    # doesn't produce one.
    # logger.debug(pp.pformat(facets))
    for fname, id_list in res['filters'].items():
        for term_id in id_list:
            if str(term_id) not in [ str(k['id']) for k in facets.get(fname, {}).get('values', []) ]:
                logger.debug("Missing: {} {}".format(fname, term_id ))
                if fname not in facets:
                    facets[fname] = {
                        "name": fname,
                        "values": [],
                    }
                missing_term = term_id
                if fname == 'library':
                    missing_term = library_dict.get(int(term_id))
                elif fname == 'creator':
                    try:
                        missing_term = Agent.objects.get(pk=term_id).name
                    except Agent.DoesNotExist:
                        missing_term = "N/A"

                facets[fname]['values'].append({
                    "count": 0,
                    "id": term_id,
                    "key": "{}{}".format(fname, term_id),
                    "term": missing_term,
                    "active": True,
                })
                # logger.debug(facets[fname]['values'])

    # logger.debug(library_dict)
    for facet in facets.values():
        fname = facet.get('name')
        active_filters = [ str(f) for f in res['filters'].get(fname) ]
        facet_terms = facet.get('values')
        for ft in facet_terms:
            if str(ft['id']) in active_filters:
                ft['active'] = True
            if fname == 'library':
                ft['term'] = library_dict.get(ft['id'], ft['term'])

        # output only the active ones
        if len(facet_terms) > 50:
            facet['values'] = [ ft for ft in facet_terms if ft.get('active') ]

    # and filter out empty facets after the pruning (too many and no active ones)
    # logger.debug(pp.pformat(facets))
    res['facets'] = { k: v for k, v in facets.items() if v.get('values') }

    if user.is_authenticated and not user.is_superuser:
        # authenticated users can set exclusion
        res['can_set_exclusions'] = True
        res['can_merge'] = user.can_merge_entries()

    def replace_codes(m):
        full, obj_name, obj_id = m.group(0, 1, 2)
        obj = None
        if obj_name == 'library':
            try:
                obj = Library.objects.get(pk=obj_id)
            except Library.DoesNotExist:
                pass
        elif obj_name == 'creator':
            try:
                obj = Agent.objects.get(pk=obj_id)
            except Library.DoesNotExist:
                pass
        if obj:
            return "{} ({})".format(obj.name, full)
        else:
            return full

    if res['querystring']:
        res['pretty_query'] = re.sub(r'(creator|library):([0-9]+)', replace_codes, res['querystring'])

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
        'description',
        'languages',
        'logo_url',
        'year_established',
        'email_public',
        'email_internal',
        'opening_hours',
        'latitude',
        'longitude',
        'short_desc',
        'pgp_public_key',
        'address_line_1',
        'address_line_2',
        'address_city',
        'address_zip',
        'address_state',
        'address_country',
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
                    if not value and f in [ 'latitude', 'longitude', 'year_established']:
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
        for agent in (Agent.objects.filter(canonical_agent_id__isnull=False)
                      .prefetch_related('canonical_agent')
                      .order_by('canonical_agent__name', 'name')
                      .all()):
            apidata = agent.as_api_dict(get_canonical=True)
            if apidata.get('canonical'):
                for f in ['id', 'name']:
                    apidata['canonical_' + f] = apidata['canonical'][f]
                merged.append(apidata)
        out['records'] = merged
        out['fields'] = [
            { 'name': 'canonical_name', 'label': 'Canonical Name' },
            { 'name': 'canonical_id', 'label': 'Canonical ID' },
            { 'name': 'name', 'label': 'Name' },
            { 'name': 'id', 'label': 'Id' },
        ]

    elif target == 'translations' and user_can_merge(request.user):
        translations = []
        for entry in (Entry.objects.filter(original_entry_id__isnull=False)
                      .prefetch_related('original_entry')
                      .order_by('original_entry__title', 'title')
                      .all()):
            apidata = entry.as_api_dict(get_original=True)
            if apidata.get('original'):
                # flatten for the table
                apidata['authors'] = '; '.join(apidata['authors'])
                apidata['languages'] = ' '.join(apidata['languages'])
                apidata['original_authors'] = '; '.join(apidata['original']['authors'])
                apidata['original_languages'] = ' '.join(apidata['original']['languages'])
                for f in ['id', 'title', 'created', 'last_modified', 'original']:
                    apidata['original_' + f] = apidata['original'][f]
                for f in ['', 'original_']:
                    if apidata[f + 'authors']:
                        apidata[f + 'title'] = "{} — {}".format(apidata[f + 'title'], apidata[f + 'authors'])
                translations.append(apidata)
            else:
                logger.debug("Got an entry without a original? " + pp.pformat(apidata))

        out['fields'] = [
            { 'name': 'original_title', 'label': 'Original Title' },
            { 'name': 'original_id', 'label': 'Original ID', 'link': 'entry' },
            { 'name': 'title', 'label': 'Title' },
            { 'name': 'id', 'label': 'ID', 'link': 'entry' },
        ]
        out['records'] = translations


    elif target == 'merged-entries' and user_can_merge(request.user):
        merged = []
        for entry in (Entry.objects
                      .prefetch_related('canonical_entry')
                      .filter(canonical_entry_id__isnull=False)
                      .order_by('canonical_entry__title', 'title')
                      .all()):
            apidata = entry.as_api_dict(get_canonical=True)
            if apidata.get('canonical'):
                # flatten for the table
                apidata['authors'] = '; '.join(apidata['authors'])
                apidata['languages'] = ' '.join(apidata['languages'])
                apidata['canonical_authors'] = '; '.join(apidata['canonical']['authors'])
                apidata['canonical_languages'] = ' '.join(apidata['canonical']['languages'])
                for f in ['id', 'title', 'created', 'last_modified', 'canonical']:
                    apidata['canonical_' + f] = apidata['canonical'][f]
                for f in ['', 'canonical_']:
                    if apidata[f + 'authors']:
                        apidata[f + 'title'] = "{} — {}".format(apidata[f + 'title'], apidata[f + 'authors'])
                merged.append(apidata)

            else:
                logger.debug("Got an entry without a canonical? " + pp.pformat(apidata))

        out['fields'] = [
            { 'name': 'canonical_title', 'label': 'Canonical Title' },
            { 'name': 'canonical_id', 'label': 'Canonical ID', 'link': 'entry' },
            { 'name': 'title', 'label': 'Title' },
            { 'name': 'id', 'label': 'ID', 'link': 'entry' },
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
                    out['number_of_records'] = validation['number_of_records']
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
            process_spreadsheet_upload.delay(spreadsheet_id)
            out['success'] = "Reindex started"
        else:
            out['error'] = "Invalid CSV"

    return JsonResponse(out)

def api_list_libraries(request):
    active_libraries = _active_libraries(request.user)
    data = [ l.public_data() for l in Library.objects.filter(id__in=active_libraries).order_by('name').all() ]
    return JsonResponse({ "libraries": data })

def api_show_library(request, library_id):
    library = {}
    active_libraries = _active_libraries(request.user)
    if library_id in active_libraries:
        library = Library.objects.get(pk=library_id).public_data()
    return JsonResponse({ "library": library })

def api_list_agents(request):
    term = request.GET.get('search')
    out = {
        "agents": [],
        "can_merge": user_can_merge(request.user),
        "warning": "",
        "matches": 0
    }
    if term:
        words = [ w for w in re.split(r'\W+', term) if w ]
        if words:
            query = Q(name__icontains=words.pop())
            while words:
                query = query & Q(name__icontains=words.pop())
            # logger.debug(query)
            rs = Agent.objects.prefetch_related('canonical_agent').order_by('name').filter(query)
            out['matches'] = rs.count()
            if out['matches'] > 100:
                out['warning'] = "Too many results, continue searching"
            else:
                out['agents'] = [ agent.as_api_dict(get_canonical=True) for agent in rs.all() ]
        else:
            out['error'] = "Please search for an author name"
    else:
        out['error'] = "Please search for an author name"
    return JsonResponse(out)

@ensure_csrf_cookie
def api_agent(request, agent_id):
    agent = Agent.objects.get(pk=agent_id)
    out = {}
    if agent:
        if request.method == 'POST' and user_can_merge(request.user):
            data = None
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                out['error'] = "Invalid JSON!";

            if data:
                log_user_operation(request.user, 'before-update-agent', agent, None)
                cols = ("first_name",
                        "middle_name",
                        "last_name",
                        "date_of_birth", "place_of_birth",
                        "date_of_death", "place_of_death",
                        "viaf_identifier")
                for c in cols:
                    setattr(agent, c, data.get(c))
                agent.save()
                log_user_operation(request.user, 'after-update-agent', agent, None)

        out['agent'] = agent.as_api_dict(get_canonical=False)
    else:
        out['error'] = "No such ID"

    return JsonResponse(out)

def api_list_pages(request, location, language):
    pages = Page.objects.filter(published=True,
                                location=location,
                                language=language).order_by('sorting').all()
    return JsonResponse({ "pages": [ p.overview() for p in pages ] })

def api_view_page(request, page_id):
    try:
        details = Page.objects.filter(published=True).get(pk=page_id).details()
    except Page.DoesNotExist:
        details = {}
    return JsonResponse({ "page": details })

def api_general(request):
    return JsonResponse(General.settings())

def confirm_existence(request, library_id, token):
    reply = ""
    library = None
    try:
        library = Library.objects.get(pk=library_id)
    except Library.DoesNotExist:
        reply = "This library does not exist"
    if library:
        if library.check_token and library.check_token == token:
            library.last_check = datetime.now(timezone.utc)
            library.check_token = ''
            library.save()
            reply = "Thanks for confirming"
        else:
            reply = "Wrong token"
    return HttpResponse(reply, content_type="text/plain")

def download_compiled_book(request, session_id):
    api_auth = { "X-AMC-API-Key": settings.AMUSECOMPILE_API_KEY }
    base_url = settings.AMUSECOMPILE_URL
    r = requests.get(base_url + '/compile/' + session_id, headers=api_auth)
    if r.status_code == 200:
        return HttpResponse(r.content,
                            content_type=r.headers['content-type'],
                            headers={
                                'Content-Disposition': r.headers['Content-Disposition']
                            })
    else:
        raise Http404("File not found!")

def api_bookbuilder(request):
    api_auth = { "X-AMC-API-Key": settings.AMUSECOMPILE_API_KEY }
    base_url = settings.AMUSECOMPILE_URL
    params = json.loads(request.body)
    action = params.get('action', '')
    # no session id needed
    if action == 'get_fonts':
        r = requests.get(base_url + '/fonts', headers=api_auth)
        return JsonResponse(r.json())
    if action == 'get_headings':
        r = requests.get(base_url + '/headings', headers=api_auth)
        return JsonResponse(r.json())
    logger.debug(params)
    amc_sid = params.get('session_id')
    if amc_sid:
        logger.debug("AMC session is " + amc_sid)
        r = requests.get("{}/check-session/{}".format(base_url, amc_sid), headers=api_auth)
        if r.json().get('error'):
            amc_sid = None

    if not amc_sid:
        r = requests.post(base_url + '/create-session', headers=api_auth)
        request.session['amc_sid'] = amc_sid
        amc_sid = r.json()['session_id']
    out = { "session_id": amc_sid }

    logger.debug("Action is " + action)
    if action == 'list':
        r = requests.get(base_url + '/list/' + amc_sid, headers=api_auth)
        out['texts'] = r.json()['texts']
    elif action == 'build':
        bbargs = params.get('collection_data')
        r = requests.post(base_url + '/compile/' + amc_sid, headers=api_auth, data=bbargs)
        out['job_id'] = r.json()['job_id']
    elif action == 'check_job':
        r = requests.get("{}/job-status/{}".format(base_url, params.get('check_job_id')), headers=api_auth)
        out['status'] = r.json()['status']
    elif action == 'add':
        # fire and forget
        requests.post(base_url + '/cleanup', headers=api_auth)
        try:
            ds = DataSource.objects.get(pk=params.get('add'))
        except DataSource.DoesNotExist:
            out['error'] = "Not found"
            return JsonResponse(out)
        site = ds.site
        if site.library_id in _active_libraries(request.user):
            if site.site_type == 'amusewiki':
                r = ds.get_remote_file('.zip')
                filename = ds.amusewiki_uri()
                logger.debug("Filename is {}".format(filename))
                files = {
                    'muse': ("{}.zip".format(filename), r.content, 'application/zip')
                }
                # logger.debug(files)
                rc = requests.post(base_url + '/add/' + amc_sid,
                                   files=files,
                                   data={'title': ds.entry.title, "entry_id": ds.entry_id, "ds_id": ds.id },
                                   headers=api_auth)
                # logger.debug(rc.request.headers)
                res = rc.json()
                logger.debug(res)
                out['status'] = res.get('status')
                out['file_id'] = res.get('file_id')
    elif action == 'remove':
        r = requests.post("{}/list/{}/remove/{}".format(base_url, amc_sid, params.get('remove_id')), headers=api_auth)
        rj = r.json()
        out['status'] = rj['status']
        out['texts'] = rj['texts']
    elif action == 'reorder':
        r = requests.post("{}/list/{}/reorder/{}/{}".format(base_url,
                                                            amc_sid,
                                                            params.get('move_id'),
                                                            params.get('to_id')),
                          headers=api_auth)
        rj = r.json()
        out['status'] = rj['status']
        out['texts'] = rj['texts']
    logger.debug(out)
    return JsonResponse(out)

def api_bookcover(request):
    api_auth = { "X-AMC-API-Key": settings.AMUSECOMPILE_API_KEY }
    base_url = settings.AMUSECOMPILE_URL
    params = json.loads(request.body)
    logger.debug(params)
    action = params.get('action', '')
    if action == 'get_tokens':
        r = requests.get(base_url + '/covers/tokens', headers=api_auth)
        return JsonResponse(r.json())
    elif action == 'build':
        r = requests.post(base_url + '/covers/build', headers=api_auth, json=params['args'])
        return JsonResponse(r.json())

# @login_required
def api_bookcover_upload_file(request):
    api_auth = { "X-AMC-API-Key": settings.AMUSECOMPILE_API_KEY }
    base_url = settings.AMUSECOMPILE_URL
    out = {}
    if request.method == 'POST':
        sid = request.POST.get('session_id')
        r = requests.get(base_url + '/covers/session/' + sid, headers=api_auth)
        res = r.json()
        upload_dir = res['upload_dir']
        for param_name, uploaded_file in request.FILES.items():
            filename = uploaded_file.name
            if re.fullmatch(r'[A-Za-z0-9].+\.(jpe?g|png)', filename):
                clean_filename = re.sub(r'[^a-zA-Z0-9\.]+', '-', filename)
                target = Path(upload_dir, clean_filename)
                logger.info("Writing {}".format(target))
                with target.open("wb+") as f:
                    for chunk in uploaded_file.chunks():
                        f.write(chunk)
                out[param_name] = clean_filename
            else:
                logger.info("Refusing to handle filename, illegal name {}".format(filename))
    return JsonResponse({ "tokens": out })


@login_required
def api_report_ds_error(request, data_source_id):
    ds = get_object_or_404(DataSource, pk=data_source_id)
    out = {}
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        out['error'] = "Invalid JSON!"
    user = request.user
    if data and data.get('message'):
        if ds.entry:
            if ds.site.library_id in _active_libraries(request.user):
                library = ds.site.library
                if library.email_internal and user.email:
                    our_name = General.settings().get('site_name')
                    original_url = "{}/entry/{}".format(settings.CANONICAL_ADDRESS,
                                                        ds.entry_id)
                    entry_title = ds.entry.title
                    subject = "[{} Error Report] {}".format(
                        our_name,
                        re.sub(r'\s+', ' ', ds.entry.title)
                    )
                    body = """
Greetings,

{} reported the following about your bibliographical entry listed at
{}

{}

Thanks
-- 
{}
{}
"""
                    report = LibraryErrorReport.objects.create(
                        user=request.user,
                        library=library,
                        message=body.format(
                            user.email, original_url, data.get('message'),
                            our_name,
                            settings.CANONICAL_ADDRESS,
                        ),
                        sender=user.email,
                        recipient=library.email_internal,
                    )
                    logger.info("Reporting {} from {} to {}".format(data.get('message'),
                                                                    report.sender,
                                                                    report.recipient))
                    email = EmailMessage(
                        subject,
                        report.message,
                        settings.MYCORRHIZA_EMAIL_FROM,
                        [report.recipient],
                        reply_to=[report.sender],
                    )
                    if email.send():
                        report.sent =  datetime.now(timezone.utc)
                        report.save()
                        out['success'] = "OK"
                    else:
                        out['error'] = "Failure sending email"

    if not out.get('success') and not out.get('error'):
        out['error'] = "Could not contact the library"
    return JsonResponse(out)
