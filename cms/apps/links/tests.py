from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from .models import Link
from ..pages.models import Page
from ... import externals


class TestLinks(TestCase):

    def setUp(self):
        with externals.watson.context_manager("update_index")():
            page = Page.objects.create(
                title="Homepage",
                content_type=ContentType.objects.get_for_model(Link),
            )

            Link.objects.create(
                page=page,
                link_url="http://www.example.com/",
            )

    def testLinkRedirect(self):
        response = self.client.get("/")
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response["Location"], "http://www.example.com/")
