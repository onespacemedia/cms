from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory

# `cms.admin` is import here and later on to test the NotRegistered exception.
import cms.admin
from ..admin import OnlineBaseAdmin
from ..models import OnlineBase

import sys


class OnlineBaseAdminTestModel(OnlineBase):
    pass


class AdminTest(TestCase):

    def setUp(self):
        factory = RequestFactory()
        self.request = factory.get('/')

        self.site = AdminSite()
        self.page_admin = OnlineBaseAdmin(OnlineBaseAdminTestModel, self.site)

    def test_onlinebaseadmin_publish_selected(self):
        obj = OnlineBaseAdminTestModel.objects.create(
            is_online=False,
        )

        self.assertFalse(obj.is_online)

        self.page_admin.publish_selected(self.request, OnlineBaseAdminTestModel.objects.all())

        obj = OnlineBaseAdminTestModel.objects.get(pk=obj.pk)
        self.assertTrue(obj.is_online)

    def test_onlinebaseadmin_unpublish_selected(self):
        obj = OnlineBaseAdminTestModel.objects.create(
            is_online=True,
        )

        self.assertTrue(obj.is_online)

        self.page_admin.unpublish_selected(self.request, OnlineBaseAdminTestModel.objects.all())

        obj = OnlineBaseAdminTestModel.objects.get(pk=obj.pk)
        self.assertFalse(obj.is_online)

    def test_user_unregister(self):
        admin.site.unregister(User)

        del sys.modules['cms.admin']
        import cms.admin
