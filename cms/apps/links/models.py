'''Content used by the links application.'''

from django.db import models

from cms.apps.pages.models import ContentBase
from cms.models import LinkField


class Link(ContentBase):

    '''A redirect to another URL.'''

    classifier = 'utilities'

    icon = 'links/img/link.png'

    urlconf = 'cms.apps.links.urls'

    robots_index = False

    link_url = LinkField(
        'link URL',
        help_text='The URL where the user will be redirected.',
    )

    new_window = models.BooleanField(
        help_text='Open the page in a new window.',
        default=False,
    )

    def __str__(self):
        return self.page.title
