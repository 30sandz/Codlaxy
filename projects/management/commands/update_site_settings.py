from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings
from allauth.account.models import EmailAddress

class Command(BaseCommand):
    help = 'Updates the site settings and cleans up example.com references'

    def handle(self, *args, **options):
        # Update the default site
        site, created = Site.objects.get_or_create(id=settings.SITE_ID)
        site.name = settings.SITE_NAME
        site.domain = settings.SITE_DOMAIN
        site.save()

        # Update any example.com email addresses in the database
        EmailAddress.objects.filter(email__endswith='@example.com').delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated site:\n'
                f'- Name: {site.name}\n'
                f'- Domain: {site.domain}\n'
                f'- Removed any @example.com email addresses'
            )
        ) 