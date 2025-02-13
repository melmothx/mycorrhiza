from .models import Site, Entry, Exclusion, Agent, User, SpreadsheetUpload
from celery import shared_task
from amwmeta.utils import log_user_operation
from django.conf import settings
from amwmeta.xapian import MycorrhizaIndexer
import logging
import pprint

logger = logging.getLogger(__name__)
pp = pprint.PrettyPrinter(indent=2)

# main router for user operations which need logging.

@shared_task
def manipulate(op, user_id, main_id, *ids, create=None):
    user = User.objects.get(pk=user_id)
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
        logger.info("Reindexing")
        indexer = MycorrhizaIndexer(db_path=settings.XAPIAN_DB)
        indexer.index_entries(reindex)
        logger.info(indexer.logs)

    return out

@shared_task
def process_spreadsheet_upload(spreadsheet_id):
    ss = SpreadsheetUpload.objects.get(pk=spreadsheet_id)
    ss.process_csv()
