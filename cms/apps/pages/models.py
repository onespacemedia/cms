'''Core models used by the CMS.'''
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django import urls
from django.db import connection, models, transaction
from django.db.models import Case, Exists, ExpressionWrapper, F, Func, OuterRef, Q, Value, When
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.functional import cached_property
from reversion.models import Version

from cms import sitemaps
from cms.models import OnlineBaseManager, PageBase, PageBaseSearchAdapter
from cms.models.managers import publication_manager


class PageManager(OnlineBaseManager):

    '''Manager for Page objects.'''

    def get_queryset(self):
        queryset = super().get_queryset().annotate(is_canonical_page=ExpressionWrapper(
            Q(owner_id__isnull=True) & Q(version_for_id__isnull=True), output_field=models.BooleanField()
        ))

        return queryset

    def select_published(self, queryset, page_alias=None):
        '''Selects only published pages.'''
        queryset = super().select_published(queryset)
        now = timezone.now().replace(second=0, microsecond=0)
        # Perform local filtering.
        queryset = queryset.filter(version_for_id__isnull=True)
        queryset = queryset.filter(
            Q(publication_date=None) | Q(publication_date__lte=now)
        )
        queryset = queryset.filter(Q(expiry_date=None) | Q(expiry_date__gt=now))

        # Perform parent ordering.
        offline_ancestors = self._queryset_class(model=self.model, using=self._db, hints=self._hints).filter(
            Q(version_for_id__isnull=True),
            Q(left__lt=OuterRef('left')) & Q(right__gt=OuterRef('right')),
            Q(country_group_id__isnull=True) | Q(country_group_id=OuterRef('country_group_id')),
            Q(is_online=False) | Q(publication_date__gt=now) | Q(expiry_date__lte=now),
        )
        queryset = queryset.annotate(parents_online=~Exists(offline_ancestors)).filter(parents_online=True)

        return queryset

    def get_homepage(self):
        '''Returns the site homepage.'''
        return self.get(parent=None, is_canonical_page=True)


not_in_tree_q = Q(left__isnull=True) & Q(right__isnull=True)
in_tree_q = Q(left__isnull=False) & Q(right__isnull=False)


class Page(PageBase):

    '''A page within the site.'''

    objects = PageManager()

    # Hierarchy fields.

    parent = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        related_name='child_set',
        on_delete=models.CASCADE,
    )

    left = models.IntegerField(
        editable=False,
        db_index=True,
        null=True,
    )

    right = models.IntegerField(
        editable=False,
        db_index=True,
        null=True,
    )

    country_group = models.ForeignKey(
        'pages.CountryGroup',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    owner = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        related_name='owner_set',
        on_delete=models.CASCADE,
    )

    version = models.IntegerField(
        default=1,
    )

    version_for = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        related_name='version_set',
        on_delete=models.CASCADE,
    )

    version_name = models.CharField(
        max_length=100,
        help_text='Used to identify this version in the admin',
        blank=True,
        null=True,
        verbose_name='draft name'
    )

    version_publication_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text='The date this version will be published',
        verbose_name='publish on',
    )

    @cached_property
    def children(self):
        '''The child pages for this page.'''
        children = []
        page = self.canonical_version
        if page.right - page.left > 1:  # Optimization - don't fetch children
            #  we know aren't there!
            for child in page.child_set.filter(is_canonical_page=True):
                child.parent = page
                children.append(child)
        return children

    @property
    def navigation(self):
        '''The sub-navigation of this page.'''
        return [child for child in self.children if child.in_navigation]

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
        on_delete=models.CASCADE,
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

    # Standard model methods.

    def get_absolute_url(self):
        '''Generates the absolute url of the page.'''

        if not self.parent:
            return urls.get_script_prefix()

        return self.parent.get_absolute_url() + self.slug + '/'

    # Tree management.

    @property
    def _branch_width(self):
        return self.right - self.left + 1

    def _excise_branch(self):
        '''Excises this whole branch from the tree.'''
        branch_width = self._branch_width
        Page.objects.filter(left__gte=self.left).update(
            left=F('left') - branch_width,
        )
        Page.objects.filter(right__gte=self.left).update(
            right=F('right') - branch_width,
        )

    def _insert_branch(self):
        '''Inserts this whole branch into the tree.'''
        branch_width = self._branch_width
        Page.objects.filter(left__gte=self.left).update(
            left=F('left') + branch_width,
        )
        Page.objects.filter(right__gte=self.left).update(
            right=F('right') + branch_width,
        )

    @transaction.atomic
    def save(self, *args, **kwargs):
        '''Saves the page.'''

        if self._is_canonical_page:
            with connection.cursor() as cursor:
                cursor.execute('LOCK TABLE {} IN ROW SHARE MODE'.format(Page._meta.db_table))

                # Lock entire table.
                existing_pages = dict(
                    (page['id'], page)
                    for page
                    in Page.objects.filter(
                        is_canonical_page=True
                    ).select_for_update().values(
                        'id',
                        'parent_id',
                        'left',
                        'right'
                    )
                )

                if self.left is None or self.right is None:
                    # This page is being inserted.
                    if existing_pages:
                        if not self.parent_id:
                            # There is no parent - we're updating the homepage.
                            # Set the parent to be the homepage by default
                            self.parent_id = Page.objects.get_homepage().pk

                        parent_right = existing_pages[self.parent_id]['right']
                        # Set the model left and right.
                        self.left = parent_right
                        self.right = self.left + 1
                        # Update the whole tree structure.
                        self._insert_branch()
                    else:
                        # This is the first page to be created, ever!
                        self.left = 1
                        self.right = 2
                else:
                    # This is an update.
                    if self.id not in existing_pages:
                        old_parent_id = -1
                    else:
                        old_parent_id = existing_pages[self.id]['parent_id']

                    if old_parent_id != self.parent_id:
                        # The page has moved.
                        branch_width = self.right - self.left + 1
                        # Disconnect child branch.
                        if branch_width > 2:
                            Page.objects.filter(
                                left__gt=self.left,
                                right__lt=self.right
                            ).update(
                                left=F('left') * -1,
                                right=F('right') * -1,
                            )
                        self._excise_branch()
                        # Store old left and right values.
                        old_left = self.left
                        old_right = self.right
                        # Put self into the tree.
                        if self.parent_id:
                            parent_right = existing_pages[self.parent_id]['right']
                            if parent_right > self.right:
                                parent_right -= self._branch_width
                            self.left = parent_right
                            self.right = self.left + branch_width - 1
                            self._insert_branch()

                            # Put all children back into the tree.
                            if branch_width > 2:
                                child_offset = self.left - old_left
                                Page.objects.filter(
                                    left__lt=-old_left,
                                    right__gt=-old_right
                                ).update(
                                    left=(F('left') - child_offset) * -1,
                                    right=(F('right') - child_offset) * -1,
                                )

        # Now actually save it!
        super().save(*args, **kwargs)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        '''Deletes the page.'''
        if self._is_canonical_page:
            list(Page.objects.filter(is_canonical_page=True).select_for_update().values_list(
                'left',
                'right',
            ))  #
            # Lock entire
            #  table.
            super().delete(*args, **kwargs)
            # Update the entire tree.
            self._excise_branch()
        else:
            super().delete(*args, **kwargs)

    def last_modified(self):
        versions = Version.objects.get_for_object(self)
        if versions.count() > 0:
            latest_version = versions[:1][0]
            return '{} by {}'.format(
                latest_version.revision.date_created.strftime('%d/%m/%Y %H:%M'),
                latest_version.revision.user
            )
        return '-'

    def get_language_pages(self):
        if self.version_for:
            return self.version_for.get_language_pages()
        if self.owner:
            return self.owner.get_language_pages()

        current_page_qs = Page.objects.filter(pk=self.pk)
        return self.owner_set.exclude(version_for_id__isnull=False).union(current_page_qs)

    def get_versions(self):
        if self.version_for_id:
            parent_page_qs = Page.objects.filter(pk=self.version_for_id)
            return self.version_for.version_set.union(parent_page_qs).order_by('version_for_id', '-version').reverse()

        current_page_qs = Page.objects.filter(pk=self.pk)
        return self.version_set.union(current_page_qs).order_by('version_for_id', '-version').reverse()

    def get_admin_url(self):
        if getattr(settings, 'PAGES_VERSIONING', False) and not self.version_for_id:
            return reverse('admin:pages_page_overview', kwargs={'object_id':self.id})
        return reverse('admin:pages_page_change', kwargs={'object_id':self.id})

    def get_preview_url(self):
        url = super().get_preview_url()
        if self.version_for_id:
            return f'{url}&version={self.version}'
        return url

    def get_public_preview_url(self):
        url = super().get_public_preview_url()
        if self.version_for_id:
            return f'{url}&version={self.version}'
        return url

    def get_language(self):
        if self.country_group:
            return str(self.country_group)
        try:
            return Country.objects.select_related('group').get(default=True).group
        except Country.DoesNotExist:
            return None

    def get_version_name(self):
        return self.version_name or f'Version {self.version}'

    @cached_property
    def canonical_version(self):
        if self.owner:
            return self.owner.canonical_version
        if self.version_for:
            return self.version_for.canonical_version
        return self

    @property
    def _is_canonical_page(self):
        # The name is due to the fact we can't clash with the qs annotation name
        return not (self.owner_id or self.version_for_id)

    class Meta:
        ordering = ('left',)

        constraints = [
            models.UniqueConstraint(
                fields=['parent', 'slug'],
                condition=Q(version_for_id__isnull=True) & Q(country_group__isnull=True),
                name='unique_page_urls',
            ),
            models.UniqueConstraint(
                fields=['country_group', 'owner'],
                condition=Q(version_for_id__isnull=True),
                name='unique_language_versions',
            ),
            models.CheckConstraint(
                check=(Q(version_for_id__isnull=False) & not_in_tree_q) | Q(version_for_id__isnull=True),
                name='versions_not_in_page_tree',
            ),
            models.CheckConstraint(
                check=(Q(owner_id__isnull=False) & not_in_tree_q) | Q(owner_id__isnull=True),
                name='translations_not_in_page_tree',
            ),
            models.CheckConstraint(
                check=(Q(version_for_id__isnull=True) & Q(owner_id__isnull=True) & in_tree_q) | Q(version_for_id__isnull=False) | Q(owner_id__isnull=False),
                name='page_mptt_values',
            )
        ]


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

        return ' '.join([
            super().get_content(obj),
            self.prepare_content(content_obj.get_searchable_text())
        ])

    def get_live_queryset(self):
        '''Selects the live page queryset.'''
        # HACK: Prevents a table name collision in the Django queryset manager.
        with publication_manager.select_published(False):
            qs = Page._base_manager.all()
        if publication_manager.select_published_active():
            qs = Page.objects.select_published(qs, page_alias='U0')
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
        on_delete=models.CASCADE,
    )

    def __str__(self):
        '''Returns a unicode representation.'''
        return self.page.title

    class Meta:
        abstract = True

    def get_searchable_text(self):
        '''
        Returns a blob of text that will be indexed by Watson. This will be
        given lower priority than the title of the page it is attached to.

        By default this will return every text field on the ContentBase,
        separated by a space. A common case for overriding this is when your
        page's content is built out of other models.
        '''
        return ' '.join([
            force_text(getattr(self, field_name))
            for field_name in [
                field.name for field
                in self._meta.fields
                if isinstance(field, (models.CharField, models.TextField))
            ]
            # Because we don't want to index "None" :)
            if getattr(self, field_name)
        ])


class Country(models.Model):
    name = models.CharField(
        max_length=256,
    )

    code = models.CharField(
        max_length=16,
    )

    group = models.ForeignKey(
        'pages.CountryGroup',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    default = models.BooleanField(
        blank=True,
        choices=[(True, 'Yes'), (None, 'No')],
        default=None,
        null=True,
        unique=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'countries'


class CountryGroup(models.Model):
    name = models.CharField(
        max_length=256
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
