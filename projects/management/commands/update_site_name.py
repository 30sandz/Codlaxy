from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings

class Command(BaseCommand):
    help = 'Updates the default site name and domain'

    def handle(self, *args, **options):
        site = Site.objects.get(id=settings.SITE_ID)
        site.name = settings.SITE_NAME
        site.domain = settings.SITE_DOMAIN
        site.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated site name to "{site.name}" and domain to "{site.domain}"'
            )
        ) 