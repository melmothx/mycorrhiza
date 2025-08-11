from django.core.management.base import BaseCommand, CommandError
from amwmeta.xapian import MycorrhizaIndexer
from collector.models import Site, Entry, Agent
from django.db.models import Q, Count
import shutil
import logging
from django.db import connection
from django.conf import settings
from pathlib import Path
import requests.exceptions
import pprint
import fcntl
import os
import re
from datetime import datetime, timezone

pp = pprint.PrettyPrinter(indent=4)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Harvest the sites"
    def add_arguments(self, parser):
        parser.add_argument("--force",
                            action="store_true", # boolean
                            help="Force a full harvest")
        parser.add_argument("--orphans",
                            action="store_true", # boolean
                            help="Reindex orphaned entries")
        parser.add_argument("--site",
                            help="Select a specific site")
        parser.add_argument("--reindex",
                            action="store_true", # boolean
                            help="Do not fetch from OAI-PMH, just rebuild the Xapian index")
        parser.add_argument("--entry",
                            help="Reindex a single entry")

    def handle(self, *args, **options):
        lock = open('.harvest.lock', 'w')
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock.write(str(os.getpid()))
        logger.debug(options)

        db_path = settings.XAPIAN_DB
        db_path_object = Path(db_path)
        if options['entry']:
            indexer = MycorrhizaIndexer(db_path=db_path)
            entry = Entry.objects.get(pk=options['entry'])
            data = entry.indexing_data()
            pp.pprint(data)
            indexer.index_record(data)
            return

        if options['orphans']:
            indexer = MycorrhizaIndexer(db_path=db_path)
            for entry in Entry.objects.annotate(Count("datasource")).filter(datasource__count=0):
                data = entry.indexing_data()
                indexer.index_record(data)
            return
        if options['reindex']:
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
            # and index the new reindexed from the site
            for entry in Entry.objects.filter(last_indexed__date__gte=now):
                indexer.index_record(entry.indexing_data())
                logger.info("Reindexing {}, it was indexed before the reindex started".format(entry.id))
            return

        rs = Site.objects.filter(active=True)
        if options['site']:
            rs = rs.filter(Q(url__contains=options['site']) | Q(title__contains=options['site']))

        for site in rs.all():
            print("Harvesting {}".format(site.title))
            try:
                site.harvest(force=options['force'])
            except requests.exceptions.HTTPError:
                print("Server error for {}, skipping".format(site.url))
            except requests.exceptions.ConnectionError:
                print("Failure on connection to {}, skipping".format(site.url))
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()
