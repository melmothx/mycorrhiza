from .models import Entry, SpreadsheetUpload
from celery import shared_task
from amwmeta.utils import log_user_operation
from django.conf import settings
from amwmeta.xapian import MycorrhizaIndexer
from datetime import datetime, timezone
from pathlib import Path
import shutil
import logging
import pprint
import re

logger = logging.getLogger(__name__)
pp = pprint.PrettyPrinter(indent=2)

@shared_task
def process_spreadsheet_upload(spreadsheet_id):
    ss = SpreadsheetUpload.objects.get(pk=spreadsheet_id)
    ids = ss.process_csv()
    xapian_index_records(ids)

@shared_task
def xapian_index_records(entry_ids):
    if not entry_ids:
        return
    indexer = MycorrhizaIndexer(db_path=settings.XAPIAN_DB)
    for eid in entry_ids:
        try:
            entry = Entry.objects.get(pk=eid)
            indexer.index_record(entry.indexing_data())
        except Entry.DoesNotExist:
            logger.info("{} does not exist".format(eid))
    indexer.close()

@shared_task
def xapian_reindex_all():
    db_path = settings.XAPIAN_DB
    db_path_object = Path(db_path)
    now = datetime.now(timezone.utc)
    stub_content = db_path_object.read_text()
    # see settings.py initialize_xapian_db
    stub_match = re.match(r'auto\s+([a-zA-Z0-9_/-]+/)(db|db1|db2)\s*$', stub_content)
    target_db = None
    if stub_match:
        db_path_dir = stub_match.group(1)
        current_db_name = stub_match.group(2)
        current_db_path = "{}{}".format(db_path_dir, current_db_name)
        switch_db = {
            "db": "db1",
            "db1": "db2",
            "db2": "db1",
        }
        target_db = "{}{}".format(db_path_dir, switch_db[current_db_name])
    else:
        raise Exception("stub.db content looks invalid: {}".format(stub_content))

    logger.info("Current db is {}, target is {}".format(current_db_path, target_db))
    if Path(target_db).is_dir():
        logger.info("Removing {}".format(target_db))
        shutil.rmtree(target_db)

    indexer = MycorrhizaIndexer(db_path=target_db)
    counter = 0
    for entry in Entry.objects.iterator():
        indexer.index_record(entry.indexing_data())
        counter += 1
        if counter % 1000 == 0:
            logger.debug(str(counter) + " records done")
    # when this is done, switch the db_path in the stub
    tmp = Path(db_path + '.tmp')
    tmp.write_text("auto {}\n".format(target_db))
    tmp.rename(db_path_object)
    # and index the new reindexed from the site, but probably not needed
    for entry in Entry.objects.filter(last_indexed__date__gte=now):
        indexer.index_record(entry.indexing_data())
        logger.info("Reindexing {}, it was indexed before the reindex started".format(entry.id))
    indexer.close()
