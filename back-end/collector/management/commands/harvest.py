from django.core.management.base import BaseCommand, CommandError
from amwmeta.xapian import MycorrhizaIndexer, XAPIAN_DB
from collector.models import Site, Entry, Agent
import shutil
import logging
from django.db import connection
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
        logger.debug(options)

        if options['force'] and not options['site']:
            try:
                print("Removing " + XAPIAN_DB)
                shutil.rmtree(XAPIAN_DB)
            except FileNotFoundError:
                pass
            if options['nuke_aliases']:
                print("Cleaning aliases")
                Agent.objects.filter(canonical_agent_id__isnull=False).update(canonical_agent=None)
                Entry.objects.filter(canonical_entry_id__isnull=False).update(canonical_entry=None)
                print(connection.queries)

        if options['entry']:
            indexer = MycorrhizaIndexer()
            entry = Entry.objects.get(pk=options['entry'])
            indexer.index_record(entry.indexing_data())
            return

        if options['reindex']:
            indexer = MycorrhizaIndexer()
            counter = 0
            for entry in Entry.objects.all():
                indexer.index_record(entry.indexing_data())
                counter += 1
                if counter % 1000 == 0:
                    logger.debug(str(counter) + " records done")
            return

        rs = Site.objects.filter(active=True, site_type__in=['amusewiki', 'generic'])
        if options['site']:
            rs = rs.filter(url__contains=options['site'])

        for site in rs.all():
            site.harvest(options['force'])
