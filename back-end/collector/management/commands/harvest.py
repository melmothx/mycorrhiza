from django.core.management.base import BaseCommand, CommandError
from amwmeta.xapian import MycorrhizaIndexer
from collector.models import Site, Entry, Agent
import shutil
import logging
from django.db import connection
from django.conf import settings
from pathlib import Path
import requests.exceptions
import pprint
import fcntl
import os

pp = pprint.PrettyPrinter(indent=4)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Harvest the sites"
    def add_arguments(self, parser):
        parser.add_argument("--force",
                            action="store_true", # boolean
                            help="Force a full harvest")
        parser.add_argument("--site",
                            help="Select a specific site")
        parser.add_argument("--reindex",
                            action="store_true", # boolean
                            help="Do not fetch from OAI-PMH, just rebuild the Xapian index")
        parser.add_argument("--nuke-aliases",
                            action="store_true",
                            help="Remove all the aliases and variant relationships (only if --force without --site)")
        parser.add_argument("--entry",
                            help="Reindex a single entry")

    def handle(self, *args, **options):
        lock = open('.harvest.lock', 'w')
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock.write(str(os.getpid()))
        logger.debug(options)

        db_path = settings.XAPIAN_DB
        db_path_object = Path(settings.XAPIAN_DB)
        if options['force'] and not options['site']:
            if db_path and db_path_object.is_dir() and db_path_object.name == 'db':
                shutil.rmtree(db_path)

            if options['nuke_aliases']:
                print("Cleaning aliases")
                Agent.objects.filter(canonical_agent_id__isnull=False).update(canonical_agent=None)
                Entry.objects.filter(canonical_entry_id__isnull=False).update(canonical_entry=None)
                print(connection.queries)

        if options['entry']:
            indexer = MycorrhizaIndexer(db_path=db_path)
            entry = Entry.objects.get(pk=options['entry'])
            data = entry.indexing_data()
            pp.pprint(data)
            indexer.index_record(data)
            return

        if options['reindex']:
            indexer = MycorrhizaIndexer(db_path=db_path)
            counter = 0
            for entry in Entry.objects.iterator():
                indexer.index_record(entry.indexing_data())
                counter += 1
                if counter % 1000 == 0:
                    logger.debug(str(counter) + " records done")
            return

        rs = Site.objects.filter(active=True)
        if options['site']:
            rs = rs.filter(url__contains=options['site'])

        for site in rs.all():
            try:
                site.harvest(force=options['force'])
            except requests.exceptions.HTTPError:
                print("Server error for {}, skipping".format(site.url))
            except requests.exceptions.ConnectionError:
                print("Failure on connection to {}, skipping".format(site.url))
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()
