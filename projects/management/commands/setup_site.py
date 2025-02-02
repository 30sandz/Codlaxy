from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings

class Command(BaseCommand):
    help = 'Setup site framework with correct domain'

    def handle(self, *args, **kwargs):
        # Get or create the default site
        site, created = Site.objects.get_or_create(id=settings.SITE_ID)
        
        # Update the domain and name
        site.domain = settings.SITE_DOMAIN
        site.name = settings.SITE_NAME
        site.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully {"created" if created else "updated"} site: {site.name} ({site.domain})'
            )
        ) 