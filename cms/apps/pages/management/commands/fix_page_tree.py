from django.core.management import BaseCommand

from ...models import Page
from cms.apps.pages.utils import mptt_fix
from cms.models.managers import publication_manager


class Command(BaseCommand):
    '''
        Removes non-cannonical pages from the MPTT tree.
        Fixes Page MPTT left and right attributes.
    '''
    def handle(self, *args, **options):
        with publication_manager.select_published(False):
            pages_not_canonical = Page.objects.filter(is_content_object=False)
            for page in pages_not_canonical:
                print(page, f'left: {page.left}, right: {page.right}')
            print(pages_not_canonical.count(), 'non-canonical pages in the MPTT tree.')
            pages_not_canonical.update(left=None, right=None)
            print('Resetting MPTT attributes for canonical pages.')
            mptt_fix()
