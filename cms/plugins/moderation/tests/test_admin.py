from django.contrib.admin.sites import AdminSite
from django.db import models
from django.test import TestCase, RequestFactory

from ..admin import ModerationAdminBase
from ..models import ModerationBase


class MockSuperUser(object):
    pk = 1

    def __init__(self, permission):
        self.permission = permission

    def has_perm(self, perm):
        return self.permission


class TestModerationAdminModel(ModerationBase):

    choice = models.CharField(
        max_length=1,
        choices=[
            (1, 'Foo'),
            (2, 'Bar'),
        ]
    )


class TestModerationAdmin(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.moderation_admin = ModerationAdminBase(TestModerationAdminModel, self.site)

        self.object = TestModerationAdminModel.objects.create()

        self.factory = RequestFactory()
        self.request = self.factory.get('/')

    def test_formfield_for_choice_field_has_permission(self):
        self.request.user = MockSuperUser(True)

        formfield = self.moderation_admin.formfield_for_choice_field(
            self.object._meta.get_field('status'),
            self.request
        )

        self.assertListEqual(
            formfield.choices,
            [(1, 'Draft'), (2, 'Submitted for approval'), (3, 'Approved')]
        )

    def test_formfield_for_choice_field_has_no_permission(self):
        self.request.user = MockSuperUser(False)

        formfield = self.moderation_admin.formfield_for_choice_field(
            self.object._meta.get_field('status'),
            self.request
        )

        self.assertListEqual(
            formfield.choices,
            [(1, 'Draft'), (2, 'Submitted for approval')]
        )
