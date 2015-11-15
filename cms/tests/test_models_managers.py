from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils.timezone import now

from .. import externals
from ..models.managers import publication_manager
from ..apps.pages.models import ContentBase, Page

from datetime import timedelta


class TestPageContentForManagers(ContentBase):
    pass


class TestFields(TestCase):

    def _create_objects(self):
        with externals.watson.context_manager("update_index")():
            content_type = ContentType.objects.get_for_model(TestPageContentForManagers)

            self.date = now()

            self.homepage = Page.objects.create(
                title="Homepage",
                slug='homepage',
                content_type=content_type,
                publication_date=self.date + timedelta(days=10),
            )

            TestPageContentForManagers.objects.create(
                page=self.homepage,
            )

    def test_publicationmanager_select_published(self):
        self._create_objects()

        with publication_manager.select_published(True):
            self.assertEqual(Page.objects.count(), 0)

        with publication_manager.select_published(False):
            self.assertEqual(Page.objects.count(), 1)

        # We need to generate an exception within the published block.
        with self.assertRaises(TypeError), \
                publication_manager.select_published(True):
            assert 1 / 'a'
