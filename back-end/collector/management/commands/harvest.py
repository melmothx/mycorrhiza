from django.core.management.base import BaseCommand, CommandError
from amwmeta.xapian import MycorrhizaIndexer, XAPIAN_DB
from collector.models import Site, Entry
import shutil
import logging
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


    def handle(self, *args, **options):
        logger.debug(options)

        if options['force'] and not options['site']:
            try:
                print("Removing " + XAPIAN_DB)
                shutil.rmtree(XAPIAN_DB)
            except FileNotFoundError:
                pass

        if options['reindex']:
            indexer = MycorrhizaIndexer()
            counter = 0
            for entry in Entry.objects.all():
                indexer.index_record(entry.indexing_data())
                counter += 1
                if counter % 1000 == 0:
                    logger.debug(str(counter) + " records done")
            return

        rs = Site.objects
        if options['site']:
            rs = rs.filter(url__contains=options['site'])

        for site in rs.all():
            site.harvest(options['force'])
