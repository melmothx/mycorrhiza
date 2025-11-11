from django.core.management.base import BaseCommand, CommandError
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
from collector.tasks import xapian_index_records, xapian_reindex_all
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
        if options['entry']:
            print("Scheduling {} for reindex".format(options['entry']))
            xapian_index_records.delay([ options['entry'] ])
            return

        if options['orphans']:
            orphans = []
            for entry in Entry.objects.alias(Count("datasource")).filter(datasource__count=0):
                orphans.append(entry.id)
            xapian_index_records.delay(orphans)
            return

        if options['reindex']:
            xapian_reindex_all.delay()
            return

        rs = Site.objects.filter(active=True)
        if options['site']:
            rs = rs.filter(Q(url__contains=options['site']) | Q(title__contains=options['site']))

        for site in rs.all():
            print("Harvesting {}".format(site.title))
            try:
                xapian_index_records.delay(site.harvest(force=options['force']))
            except requests.exceptions.HTTPError:
                print("Server error for {}, skipping".format(site.url))
            except requests.exceptions.ConnectionError:
                print("Failure on connection to {}, skipping".format(site.url))
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()
