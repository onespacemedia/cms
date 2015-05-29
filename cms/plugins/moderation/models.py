from django.db import models

from cms.models.managers import PublishedBaseManager

DRAFT = 1
SUBMITTED = 2
APPROVED = 3

STATUS_CHOICES = [
    (DRAFT, 'Draft'),
    (SUBMITTED, 'Submitted for approval'),
    (APPROVED, 'Approved')
]


class ModerationManager(PublishedBaseManager):

    def select_published(self, queryset):
        queryset = super(ModerationManager, self).select_published(queryset)

        return queryset.filter(
            status=APPROVED,
        )


class ModerationBase(models.Model):

    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=DRAFT,
    )

    objects = ModerationManager()

    class Meta:
        abstract = True
        permissions = (
            ("can_approve", "Can approve items"),
        )
