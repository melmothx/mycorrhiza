from .models import Entry, SpreadsheetUpload
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
def process_spreadsheet_upload(spreadsheet_id):
    ss = SpreadsheetUpload.objects.get(pk=spreadsheet_id)
    ss.process_csv()

@shared_task
def xapian_index_records(entry_ids):
    indexer = MycorrhizaIndexer(db_path=settings.XAPIAN_DB)
    for eid in entry_ids:
        try:
            entry = Entry.objects.get(pk=eid)
            indexer.index_record(entry.indexing_data())
        except Entry.DoesNotExist:
            logger.info("{} does not exist".format(eid))
