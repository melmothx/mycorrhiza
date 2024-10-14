from django.core.management.base import BaseCommand, CommandError
from collector.models import Library, General
from django.db.models import Q
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Send mail to confirm library existence"

    def handle(self, *args, **options):
        refdate = datetime.now(timezone.utc) - timedelta(days=90)
        rs = Library.objects.filter(
            Q(last_check__lte=refdate) | Q(last_check__isnull=True),
            Q(email_internal__contains='@') | Q(email_public__contains='@'),
            enable_check=True,
            check_token="",
        )
        mail_from = settings.MYCORRHIZA_EMAIL_FROM
        site_name = General.objects.get(name="site_name").value
        for lib in rs.all():
            recipient = lib.email_internal
            if '@' not in recipient:
                recipient = lib.email_public

            if recipient:
                lib.check_token = token_urlsafe(16)
                lib.save()
                url = reverse('confirm_existence', args=[lib.id, lib.check_token])
                send_mail("{}: please confirm you are monitoring this email".format(site_name),
                          "Please visit {}{} to confirm it".format(settings.CANONICAL_ADDRESS, url),
                          settings.MYCORRHIZA_EMAIL_FROM,
                          [ recipient ])
