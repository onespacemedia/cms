from django.db import models

from cms.plugins.moderation.models import ModerationBase


class TestModerationAdminModel(ModerationBase):

    choice = models.CharField(
        max_length=1,
        choices=[
            (1, 'Foo'),
            (2, 'Bar'),
        ]
    )
