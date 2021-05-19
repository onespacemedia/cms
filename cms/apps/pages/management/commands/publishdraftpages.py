from django.core.management import BaseCommand
from django.utils.timezone import now

from cms.apps.pages.utils import publish_page
from ...models import publication_manager, Page


class Command(BaseCommand):
    '''
        Removes non-cannonical pages from the MPTT tree.
        Fixes Page MPTT left and right attributes.
    '''
    def handle(self, *args, **options):
        with publication_manager.select_published(False):
            pages = Page.objects.filter(version_for_id__isnull=False, version_publication_date__lte=now())
            for page in pages:
                publish_page(page)
