import random
from datetime import timedelta

import pytest
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.test import TestCase
from django.utils.timezone import now

from .. import externals
from ..apps.pages.models import ContentBase, Page
from ..models.managers import publication_manager


class TestPageContentForManagers(ContentBase):
    pass


@pytest.mark.django_db(transaction=True)
class TestFields(TestCase):

    def test_publicationmanager_select_published(self):
        with externals.watson.context_manager("update_index")():
            content_type = ContentType.objects.get_for_model(TestPageContentForManagers)

            self.date = now()

            with connection.cursor() as cursor:
                cursor.execute('TRUNCATE {} CASCADE'.format(Page._meta.db_table))

            print Page.objects.count()

            self.homepage = Page.objects.create(
                pk=random.randint(100, 200000),
                title="Homepage",
                slug='homepage',
                parent=None,
                content_type=content_type,
                publication_date=self.date + timedelta(days=10),
            )

            TestPageContentForManagers.objects.create(
                page=self.homepage,
            )

        with publication_manager.select_published(True):
            self.assertEqual(Page.objects.count(), 0)

        with publication_manager.select_published(False):
            self.assertEqual(Page.objects.count(), 1)

        # We need to generate an exception within the published block.
        with self.assertRaises(TypeError), \
                publication_manager.select_published(True):
            assert 1 / 'a'
