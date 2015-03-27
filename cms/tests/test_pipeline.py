from django.http import HttpResponse
from django.test import TestCase

from ..pipeline import make_staff


class Backend(object):
    name = None

    def __init__(self, name, *args, **kwargs):
        super(Backend, self).__init__(*args, **kwargs)
        self.name = name


class MockSuperUser(object):
    is_staff = False
    is_superuser = False

    def save(self):
        pass


class PipelineTest(TestCase):

    def test_make_staff(self):
        facebook_backend = Backend('facebook')
        google_plus_backend = Backend('google-plus')
        user = MockSuperUser()
        response = HttpResponse()

        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

        make_staff(facebook_backend, user, response)

        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

        make_staff(google_plus_backend, user, response)

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
