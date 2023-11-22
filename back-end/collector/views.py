# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
import json
from amwmeta.xapian import search
import logging
from django.urls import reverse
from amwmeta.utils import paginator, page_list
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Work, Agent
from amwmeta.xapian import MycorrhizaIndexer

logger = logging.getLogger(__name__)

def api(request):
    res = search(request.GET)
    res['total_entries'] = res['pager'].total_entries
    res['pager'] = page_list(res['pager'])
    res['is_authenticated'] = request.user.is_authenticated
    return JsonResponse(res)

@csrf_exempt
@login_required
def api_merge(request, target):
    logger.debug(target)
    out = {}
    data = None
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        out['error'] = "Invalid JSON";

    if data:
        logger.debug(data)
        aliases = []
        abort = False

        if target == 'works':
            for pk in [ x['work_id'] for x in data ]:
                try:
                    alias = Work.objects.get(pk=pk)
                    aliases.append(alias)
                except Work.DoesNotExist:
                    logger.debug("Invalid work " + pk)
                    abort = True
            if abort:
                out['error'] = "Invalid argument"
            elif len(aliases) < 2:
                out['error'] = "Missing arguments (at least 2)"
            else:
                canonical = aliases[0]
                canonical.canonical_work = None
                canonical.save()

                reindex = aliases[:]
                for aliased in aliases[1:]:
                    aliased.canonical_work = canonical
                    aliased.save()
                    for vw in aliased.variant_works.all():
                        vw.canonical_work = canonical
                        vw.save()
                        reindex.append(vw)

                indexer = MycorrhizaIndexer()
                for w in reindex:
                    indexer.index_record(w.indexing_data())
                logger.info(indexer.logs)
                out['success'] = "Merged!"
                # now reindex



        elif target == 'authors':
            # receiving the list
            for name in data:
                try:
                    alias = Agent.objects.get(name=name)
                    aliases.append(alias)
                except Agent.DoesNotExist:
                    logger.debug("Invalid name " + name)
                    abort = True
            if abort:
                out['error'] = "Invalid argument"
            elif len(aliases) < 2:
                out['error'] = "Missing arguments (at least 2)"
            else:
                canonical = aliases[0]
                canonical.canonical_agent = None
                canonical.save()

                reindex = aliases[:]

                for aliased in aliases[1:]:
                    aliased.canonical_agent = canonical
                    aliased.save()
                    for av in aliased.variant_agents.all():
                        av.canonical_agent = canonical
                        av.save()
                        reindex.append(av)

                indexer = MycorrhizaIndexer()
                for agent in reindex:
                    for work in agent.authored_works.all():
                        indexer.index_record(work.indexing_data())
                logger.debug(indexer.logs)
                out['success'] = "Merged!"

        else:
            out['error'] = 'Invalid path'
    logger.debug(out)
    return JsonResponse(out)
