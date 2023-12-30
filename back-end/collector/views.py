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
from .models import Entry, Agent, Site, SpreadsheetUpload
from amwmeta.xapian import MycorrhizaIndexer
from .forms import SpreadsheetForm
from django.contrib import messages
from http import HTTPStatus

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

def api(request):
    public_only = True
    exclusions = []
    active_sites = { site.id: site.public and site.active for site in Site.objects.all() }
    can_set_exclusions = False
    if request.user.is_authenticated:
        public_only = False
        exclusions = []
        for exclusion in request.user.exclusions.all():
            exclusions.extend(exclusion.as_xapian_queries())
        logger.debug("Exclusions: {}".format(exclusions))
        can_set_exclusions = True

    res = search(
        request.GET,
        public_only=public_only,
        active_sites=active_sites,
        exclusions=exclusions,
    )
    res['total_entries'] = res['pager'].total_entries
    res['pager'] = page_list(res['pager'])
    res['is_authenticated'] = not public_only
    res['can_set_exclusions'] = can_set_exclusions
    return JsonResponse(res)

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
                if what in [ 'author', 'entry', 'site' ]:
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
        queryset = Site.objects.filter(active=True).order_by("url")
    else:
        queryset = user.profile.sites.filter(active=True).order_by("url")

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
