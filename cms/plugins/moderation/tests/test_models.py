from django.test import TestCase

from ..models import ModerationBase
from ....models import publication_manager


class TestModerationModelsModel(ModerationBase):
    pass


class TestModerationModels(TestCase):

    def setUp(self):
        TestModerationModelsModel.objects.create(status=1)
        TestModerationModelsModel.objects.create(status=2)
        TestModerationModelsModel.objects.create(status=3)

    def test_moderation_manager_select_published(self):
        with publication_manager.select_published(True):
            self.assertEqual(TestModerationModelsModel.objects.count(), 1)

        with publication_manager.select_published(False):
            self.assertEqual(TestModerationModelsModel.objects.count(), 3)
