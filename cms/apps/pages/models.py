'''Core models used by the CMS.'''
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django import urls
from django.db import connection, models, transaction
from django.db.models import F, Q
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.functional import cached_property
from historylinks import shortcuts as historylinks
from mptt.models import MPTTModel, TreeForeignKey, TreeManager
from reversion.models import Version

from cms import sitemaps
from cms.models import OnlineBaseManager, PageBase, PageBaseSearchAdapter
from cms.models.managers import publication_manager


class PageManager(OnlineBaseManager):
    '''Manager for Page objects.'''

    def select_published(self, queryset, page_alias=None):
        '''Selects only published pages.'''
        queryset = super().select_published(queryset)
        now = timezone.now().replace(second=0, microsecond=0)
        # Perform local filtering.
        queryset = queryset.filter(
            Q(publication_date=None) | Q(publication_date__lte=now))
        queryset = queryset.filter(Q(expiry_date=None) | Q(expiry_date__gt=now))
        # Perform parent ordering.
        quote_name = connection.ops.quote_name
        page_alias = page_alias or quote_name('pages_page')
        queryset = queryset.extra(
            where=('''
                NOT EXISTS (
                    SELECT *
                    FROM {pages_page} AS {ancestors}
                    WHERE
                        {ancestors}.{left} < {page_alias}.{left} AND
                        {ancestors}.{right} > {page_alias}.{right} AND (
                            {ancestors}.{country_group_id} = {page_alias}.{country_group_id} OR
                            {ancestors}.{country_group_id} IS NULL
                        ) AND (
                            {ancestors}.{is_online} = FALSE OR
                            {ancestors}.{publication_date} > %s OR
                            {ancestors}.{expiry_date} <= %s
                        )
                )
            '''.format(
                page_alias=page_alias,
                **dict(
                    (name, quote_name(name))
                    for name in (
                        'pages_page',
                        'ancestors',
                        'left',
                        'right',
                        'country_group_id',
                        'is_online',
                        'publication_date',
                        'expiry_date',
                    )
                )
            ),),
            params=(now, now),
        )
        return queryset


class Page(MPTTModel, PageBase):
    '''A page within the site.'''

    objects = TreeManager()
    published_objects = PageManager()

    # Hierarchy fields.

    parent = TreeForeignKey(
        'self',
        blank=True,
        null=True,
        related_name='child_set',
    )

    left = models.IntegerField(
        editable=False,
        db_index=True,
    )

    right = models.IntegerField(
        editable=False,
        db_index=True,
    )

    is_content_object = models.BooleanField(
        default=False
    )

    country_group = models.ForeignKey(
        'pages.CountryGroup',
        blank=True,
        null=True
    )

    owner = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        related_name='owner_set',
    )

    # Publication fields.

    publication_date = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        help_text='The date that this page will appear on the website.  Leave '
                  'this blank to immediately publish this page.',
    )

    expiry_date = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        help_text='The date that this page will be removed from the website.  '
                  'Leave this blank to never expire this page.',
    )

    # Navigation fields.

    in_navigation = models.BooleanField(
        'add to navigation',
        default=True,
        help_text='Uncheck this box to remove this content from the site '
                  'navigation.',
    )

    # Content fields.

    content_type = models.ForeignKey(
        ContentType,
        editable=False,
        help_text='The type of page content.',
    )

    requires_authentication = models.BooleanField(
        default=False,
        help_text='Visitors will need to be logged in to see this page'
    )

    hide_from_anonymous = models.BooleanField(
        'show to logged in only',
        default=False,
        help_text="Visitors that aren't logged in won't see this page in the navigation"
    )

    class Meta:
        unique_together = (('parent', 'slug', 'country_group'),)
        ordering = ('left',)

    class MPTTMeta:
        right_attr = 'right'
        left_attr = 'left'

    def save(self, *args, **kwargs):
        super(Page, self).save(*args, **kwargs)
        Page.objects.rebuild()

    def get_absolute_url(self):
        if not self.parent:
            return urls.get_script_prefix()

        return self.parent.get_absolute_url() + self.slug + '/'

    @cached_property
    def children(self):
        '''The child pages for this page.'''
        children = []
        if self.right - self.left > 1:  # Optimization - don't fetch children
            #  we know aren't there!
            for child in self.child_set.filter(is_content_object=False):
                child.parent = self
                children.append(child)
        return children

    @property
    def navigation(self):
        '''The sub-navigation of this page.'''
        return [child for child in self.children if child.in_navigation]

    def auth_required(self):
        if self.requires_authentication or not self.parent:
            return self.requires_authentication
        return self.parent.auth_required()

    @cached_property
    def content(self):
        '''The associated content model for this page.'''
        content_cls = ContentType.objects.get_for_id(
            self.content_type_id).model_class()
        content = content_cls._default_manager.get(page=self)
        content.page = self
        return content

    def reverse(self, view_func, args=None, kwargs=None):
        '''Performs a reverse URL lookup.'''
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}
        urlconf = ContentType.objects.get_for_id(
            self.content_type_id
        ).model_class().urlconf

        return self.get_absolute_url().rstrip('/') + urls.reverse(
            view_func,
            args=args,
            kwargs=kwargs,
            urlconf=urlconf,
        )

    def last_modified(self):
        versions = Version.objects.get_for_object(self)
        if versions.count() > 0:
            latest_version = versions[:1][0]
            return '{} by {}'.format(
                latest_version.revision.date_created.strftime('%Y-%m-%d %H:%M:%S'),
                latest_version.revision.user
            )
        return '-'

    class Meta:
        unique_together = (('parent', 'slug', 'country_group'),)
        ordering = ('left',)


historylinks.register(Page)


class PageSitemap(sitemaps.PageBaseSitemap):

    '''Sitemap for page models.'''

    model = Page

    def items(self):
        '''Only lists items that are marked as indexable.'''
        return filter_indexable_pages(super().items())


sitemaps.register(Page, sitemap_cls=PageSitemap)


class PageSearchAdapter(PageBaseSearchAdapter):

    '''Search adapter for Page models.'''

    def get_content(self, obj):
        '''Returns the search text for the page.'''
        content_obj = obj.content

        return ' '.join((
            super().get_content(obj),
            self.prepare_content(' '.join(
                force_text(self._resolve_field(content_obj, field_name))
                for field_name in (
                    field.name for field
                    in content_obj._meta.fields
                    if isinstance(field, (models.CharField, models.TextField))
                )
            ))
        ))

    def get_live_queryset(self):
        '''Selects the live page queryset.'''
        # HACK: Prevents a table name collision in the Django queryset manager.
        with publication_manager.select_published(False):
            qs = Page._base_manager.all()
        if publication_manager.select_published_active():
            qs = Page.published_objects.select_published(qs, page_alias='U0')
        # Filter out unindexable pages.
        qs = filter_indexable_pages(qs)
        # All done!
        return qs


# Base content class.

def get_registered_content():
    '''Returns a list of all registered content objects.'''
    return [
        model for model in apps.get_models()
        if issubclass(model, ContentBase) and not model._meta.abstract
    ]


def filter_indexable_pages(queryset):
    '''
    Filters the given queryset of pages to only contain ones that should be
    indexed by search engines.
    '''
    return queryset.filter(
        robots_index=True,
        content_type__in=[
            ContentType.objects.get_for_model(content_model)
            for content_model
            in get_registered_content()
            if content_model.robots_index
        ]
    )


class ContentBase(models.Model):

    '''Base class for page content.'''

    # This must be a 64 x 64 pixel image.
    icon = 'pages/img/content.png'

    # The heading that the admin places this content under.
    classifier = 'content'

    # The urlconf used to power this content's views.
    urlconf = 'cms.apps.pages.urls'

    # A fieldset definition. If blank, one will be generated.
    fieldsets = None

    # Whether pages of this type should be included in search indexes. (Can
    # still be disabled on a per-page basis).
    robots_index = True

    page = models.OneToOneField(
        Page,
        primary_key=True,
        editable=False,
        related_name='+',
    )

    def __str__(self):
        '''Returns a unicode representation.'''
        return self.page.title

    class Meta:
        abstract = True


class Country(models.Model):
    name = models.CharField(
        max_length=256
    )

    code = models.CharField(
        max_length=16
    )

    group = models.ForeignKey(
        'pages.CountryGroup',
        blank=True,
        null=True
    )

    default = models.NullBooleanField(
        default=None,
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'countries'


class CountryGroup(models.Model):
    name = models.CharField(
        max_length=256
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
