from django.core.management.base import BaseCommand, CommandError
from amwmeta.xapian import XAPIAN_DB
from search.models import Site
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


    def handle(self, *args, **options):
        if options['force'] and not options['site']:
            try:
                print("Removing " + XAPIAN_DB)
                shutil.rmtree(XAPIAN_DB)
            except FileNotFoundError:
                pass
        rs = Site.objects
        logger.debug(options)
        if options['site']:
            rs = rs.filter(url__contains=options['site'])

        for site in rs.all():
            site.harvest(options['force'])
