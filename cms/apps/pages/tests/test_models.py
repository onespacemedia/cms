"""Tests for the pages app."""

from django.db import models
from django.test import TestCase
from django.core.management import call_command
from django.contrib.contenttypes.models import ContentType

from ..models import filter_indexable_pages, ContentBase, Page, PageSearchAdapter, PageSitemap
from .... import externals
from ....models.managers import publication_manager


class TestPageContent(ContentBase):

    urlconf = 'cms.apps.pages.tests.urls'


class TestPageContentWithSections(ContentBase):
    pass


class Section(models.Model):

    page = models.ForeignKey(Page)

    title = models.CharField(
        max_length=100,
    )


class TestPage(TestCase):

    def setUp(self):
        call_command('installwatson')

        with externals.watson.context_manager("update_index")():
            content_type = ContentType.objects.get_for_model(TestPageContent)

            self.homepage = Page.objects.create(
                title="Homepage",
                slug='homepage',
                content_type=content_type,
            )

            TestPageContent.objects.create(
                page=self.homepage,
            )

            self.section = Page.objects.create(
                parent=self.homepage,
                title="Section",
                content_type=content_type,
            )

            TestPageContent.objects.create(
                page=self.section,
            )

            self.subsection = Page.objects.create(
                parent=self.section,
                title="Subsection",
                content_type=content_type,
            )

            TestPageContent.objects.create(
                page=self.subsection,
            )

            self.subsubsection = Page.objects.create(
                parent=self.subsection,
                title="Subsubsection",
                content_type=content_type,
            )

            TestPageContent.objects.create(
                page=self.subsubsection,
            )

    def testChildPrefetching(self):
        # Make sure that prefetching works to two levels deep.
        with self.assertNumQueries(3):
            homepage = Page.objects.get_homepage()

        with self.assertNumQueries(2):
            subsection = homepage.children[0].children[0]
        self.assertEqual(subsection.title, "Subsection")

        with self.assertNumQueries(0):
            subsection = homepage.navigation[0].navigation[0]
        self.assertEqual(subsection.title, "Subsection")

        # Make sure that, beyond this, it doesn't go  pathalogical.
        with self.assertNumQueries(1):
            subsubsection = subsection.children[0]
        self.assertEqual(subsubsection.title, "Subsubsection")

        with self.assertNumQueries(0):
            subsubsection = subsection.children[0]
        self.assertEqual(subsubsection.title, "Subsubsection")

    def test_page_reverse(self):
        url = self.homepage.reverse('detail', kwargs={
            'slug': self.homepage.slug
        })

        self.assertEqual(url, '/homepage/')

        url = self.homepage.reverse('index')

        self.assertEqual(url, '/')

    def test_filter_indexable_pages(self):
        pages = Page.objects.all()
        self.assertEqual(len(pages), 4)

        pages = filter_indexable_pages(Page.objects.all())
        self.assertEqual(len(pages), 4)

        # Turn off indexing on the homepage.
        self.homepage.robots_index = False
        self.homepage.save()

        pages = filter_indexable_pages(Page.objects.all())
        self.assertEqual(len(pages), 3)

    def test_pagesitemap_items(self):
        sitemap = PageSitemap()
        self.assertEqual(len(sitemap.items()), 4)

        # Turn off indexing on the homepage.
        self.homepage.robots_index = False
        self.homepage.save()

        self.assertEqual(len(sitemap.items()), 3)

    def test_contentbase_unicode(self):
        self.assertEqual(self.homepage.content.__str__(), 'Homepage')
        self.assertEqual(self.section.content.__str__(), 'Section')
        self.assertEqual(self.subsection.content.__str__(), 'Subsection')
        self.assertEqual(self.subsubsection.content.__str__(), 'Subsubsection')

    def test_pagesearchadapter_get_live_queryset(self):
        self.assertEqual(len(externals.watson.search("Homepage", models=(Page,))), 1)

        with publication_manager.select_published(True):
            self.assertEqual(len(externals.watson.search("Homepage", models=(Page,))), 1)

            self.homepage.is_online = False
            self.homepage.save()

            self.assertEqual(len(externals.watson.search("Homepage", models=(Page,))), 0)

    def test_page_get_absolute_url(self):
        with externals.watson.context_manager("update_index")():
            Page.objects.all().delete()

            content_type = ContentType.objects.get_for_model(TestPageContent)

            new_page = Page(
                content_type=content_type,
                parent=None,
                left=None,
                right=None,
            )
            self.assertIsNone(new_page.cached_url)
            new_page.save()
            self.assertEqual(new_page.cached_url, '/')

            TestPageContent.objects.create(
                page=new_page,
            )

        self.assertEqual(new_page.get_absolute_url(), '/')
        self.assertEqual(new_page.get_absolute_url(True), '/')

        new_page = Page.objects.get(pk=new_page.pk)
        self.assertEqual(new_page.cached_url, '/')
        self.assertEqual(new_page.get_absolute_url(), '/')


class TestSectionPage(TestCase):

    def setUp(self):
        with externals.watson.context_manager("update_index")():
            content_type = ContentType.objects.get_for_model(TestPageContentWithSections)

            self.homepage = Page.objects.create(
                title="Homepage",
                slug='homepage',
                content_type=content_type,
            )

            TestPageContentWithSections.objects.create(
                page=self.homepage,
            )

    def test_pagesearchadapter_get_content(self):
        search_adapter = PageSearchAdapter(Page)

        content = search_adapter.get_content(self.homepage)
        self.assertEqual(content, "      homepage Homepage  / ")


class TestPageComplex(TestCase):

    """
    Page structure:

                                  Homepage
                                     |
                  +------------------+-----------------------+
                  |                  |                       |
           Tree 1 - Page 1    Tree 2 - Page 1         Tree 3 - Page 1
                  |                                          |
       +----------+----------+                    +----------+----------+
       |                     |                    |                     |
 Tree 1 - Page 2      Tree 1 - Page 3      Tree 3 - Page 2       Tree 3 - Page 3
                                                  |
                                       +----------+----------+
                                       |                     |
                                Tree 3 - Page 4       Tree 3 - Page 5

    """

    def setUp(self):
        structure = {
            'title': 'Homepage',
            'children': [
                {
                    'title': 'Tree 1 - Page 1',
                    'children': [
                        {
                            'title': 'Tree 1 - Page 2'
                        },
                        {
                            'title': 'Tree 1 - Page 3'
                        }
                    ]
                },
                {
                    'title': 'Tree 2 - Page 1'
                },
                {
                    'title': 'Tree 3 - Page 1',
                    'children': [
                        {
                            'title': 'Tree 3 - Page 2',
                            'children': [
                                {
                                    'title': 'Tree 3 - Page 4'
                                },
                                {
                                    'title': 'Tree 3 - Page 5'
                                }
                            ]
                        },
                        {
                            'title': 'Tree 3 - Page 3'
                        }
                    ]
                }
            ]
        }

        content_type = ContentType.objects.get_for_model(TestPageContent)
        self.page_ids = {}
        self.pages = {}

        def _add_page(page, parent=None):
            slug = page['title'].replace(' ', '_').replace('-', '_')

            page_obj = Page.objects.create(
                title=page['title'],
                slug=slug,
                content_type=content_type,
                parent=parent,
            )

            TestPageContent.objects.create(
                page=page_obj,
            )

            self.page_ids[slug] = page_obj.pk

            if page.get('children', None):
                for child in page['children']:
                    _add_page(child, page_obj)

        with externals.watson.context_manager("update_index")():
            _add_page(structure)
            self._rebuild_page_dict()

    def _rebuild_page_dict(self):
        self.pages = {}
        for page in self.page_ids:
            try:
                self.pages[page] = Page.objects.get(pk=self.page_ids[page])
            # Handle tests involving deletions.
            except Page.DoesNotExist:
                pass

    def test_page_excise_branch(self):
        # Excising a branch which hasn't been deleted should have no affect.
        self.assertEqual(self.pages['Homepage'].left, 1)
        self.assertEqual(self.pages['Homepage'].right, 20)
        self.assertEqual(self.pages['Tree_1___Page_1'].left, 2)
        self.assertEqual(self.pages['Tree_1___Page_1'].right, 7)
        self.assertEqual(self.pages['Tree_1___Page_2'].left, 3)
        self.assertEqual(self.pages['Tree_1___Page_2'].right, 4)
        self.assertEqual(self.pages['Tree_1___Page_3'].left, 5)
        self.assertEqual(self.pages['Tree_1___Page_3'].right, 6)
        self.assertEqual(self.pages['Tree_2___Page_1'].left, 8)
        self.assertEqual(self.pages['Tree_2___Page_1'].right, 9)
        self.assertEqual(self.pages['Tree_3___Page_1'].left, 10)
        self.assertEqual(self.pages['Tree_3___Page_1'].right, 19)
        self.assertEqual(self.pages['Tree_3___Page_2'].left, 11)
        self.assertEqual(self.pages['Tree_3___Page_2'].right, 16)
        self.assertEqual(self.pages['Tree_3___Page_3'].left, 17)
        self.assertEqual(self.pages['Tree_3___Page_3'].right, 18)
        self.assertEqual(self.pages['Tree_3___Page_4'].left, 12)
        self.assertEqual(self.pages['Tree_3___Page_4'].right, 13)
        self.assertEqual(self.pages['Tree_3___Page_5'].left, 14)
        self.assertEqual(self.pages['Tree_3___Page_5'].right, 15)

        self.pages['Homepage']._excise_branch()

        self.assertEqual(self.pages['Homepage'].left, 1)
        self.assertEqual(self.pages['Homepage'].right, 20)
        self.assertEqual(self.pages['Tree_1___Page_1'].left, 2)
        self.assertEqual(self.pages['Tree_1___Page_1'].right, 7)
        self.assertEqual(self.pages['Tree_1___Page_2'].left, 3)
        self.assertEqual(self.pages['Tree_1___Page_2'].right, 4)
        self.assertEqual(self.pages['Tree_1___Page_3'].left, 5)
        self.assertEqual(self.pages['Tree_1___Page_3'].right, 6)
        self.assertEqual(self.pages['Tree_2___Page_1'].left, 8)
        self.assertEqual(self.pages['Tree_2___Page_1'].right, 9)
        self.assertEqual(self.pages['Tree_3___Page_1'].left, 10)
        self.assertEqual(self.pages['Tree_3___Page_1'].right, 19)
        self.assertEqual(self.pages['Tree_3___Page_2'].left, 11)
        self.assertEqual(self.pages['Tree_3___Page_2'].right, 16)
        self.assertEqual(self.pages['Tree_3___Page_3'].left, 17)
        self.assertEqual(self.pages['Tree_3___Page_3'].right, 18)
        self.assertEqual(self.pages['Tree_3___Page_4'].left, 12)
        self.assertEqual(self.pages['Tree_3___Page_4'].right, 13)
        self.assertEqual(self.pages['Tree_3___Page_5'].left, 14)
        self.assertEqual(self.pages['Tree_3___Page_5'].right, 15)

    def test_page_save__create_with_sides(self):
        with externals.watson.context_manager("update_index")():
            content_type = ContentType.objects.get_for_model(TestPageContent)

            # Create a page with a manual left and right defined.
            page_obj = Page.objects.create(
                title='Foo',
                content_type=content_type,
                parent=self.pages['Tree_1___Page_1'],
                left=7,
                right=8,
            )

            TestPageContent.objects.create(
                page=page_obj,
            )

            self.assertEqual(page_obj.title, 'Foo')

    def test_page_save__move_branch_left(self):
        self.assertEqual(self.pages['Homepage'].left, 1)
        self.assertEqual(self.pages['Homepage'].right, 20)
        self.assertEqual(self.pages['Tree_1___Page_1'].left, 2)
        self.assertEqual(self.pages['Tree_1___Page_1'].right, 7)
        self.assertEqual(self.pages['Tree_1___Page_2'].left, 3)
        self.assertEqual(self.pages['Tree_1___Page_2'].right, 4)
        self.assertEqual(self.pages['Tree_1___Page_3'].left, 5)
        self.assertEqual(self.pages['Tree_1___Page_3'].right, 6)
        self.assertEqual(self.pages['Tree_2___Page_1'].left, 8)
        self.assertEqual(self.pages['Tree_2___Page_1'].right, 9)
        self.assertEqual(self.pages['Tree_3___Page_1'].left, 10)
        self.assertEqual(self.pages['Tree_3___Page_1'].right, 19)
        self.assertEqual(self.pages['Tree_3___Page_2'].left, 11)
        self.assertEqual(self.pages['Tree_3___Page_2'].right, 16)
        self.assertEqual(self.pages['Tree_3___Page_3'].left, 17)
        self.assertEqual(self.pages['Tree_3___Page_3'].right, 18)
        self.assertEqual(self.pages['Tree_3___Page_4'].left, 12)
        self.assertEqual(self.pages['Tree_3___Page_4'].right, 13)
        self.assertEqual(self.pages['Tree_3___Page_5'].left, 14)
        self.assertEqual(self.pages['Tree_3___Page_5'].right, 15)

        self.pages['Tree_3___Page_1'].parent = self.pages['Tree_1___Page_1']
        self.pages['Tree_3___Page_1'].save()

        # Rebuild page dict.
        self._rebuild_page_dict()

        self.assertEqual(self.pages['Homepage'].left, 1)
        self.assertEqual(self.pages['Homepage'].right, 20)
        self.assertEqual(self.pages['Tree_1___Page_1'].left, 2)
        self.assertEqual(self.pages['Tree_1___Page_1'].right, 17)
        self.assertEqual(self.pages['Tree_1___Page_2'].left, 3)
        self.assertEqual(self.pages['Tree_1___Page_2'].right, 4)
        self.assertEqual(self.pages['Tree_1___Page_3'].left, 5)
        self.assertEqual(self.pages['Tree_1___Page_3'].right, 6)
        self.assertEqual(self.pages['Tree_2___Page_1'].left, 18)
        self.assertEqual(self.pages['Tree_2___Page_1'].right, 19)
        self.assertEqual(self.pages['Tree_3___Page_1'].left, 7)
        self.assertEqual(self.pages['Tree_3___Page_1'].right, 16)
        self.assertEqual(self.pages['Tree_3___Page_2'].left, 8)
        self.assertEqual(self.pages['Tree_3___Page_2'].right, 13)
        self.assertEqual(self.pages['Tree_3___Page_3'].left, 14)
        self.assertEqual(self.pages['Tree_3___Page_3'].right, 15)
        self.assertEqual(self.pages['Tree_3___Page_4'].left, 9)
        self.assertEqual(self.pages['Tree_3___Page_4'].right, 10)
        self.assertEqual(self.pages['Tree_3___Page_5'].left, 11)
        self.assertEqual(self.pages['Tree_3___Page_5'].right, 12)

    def test_page_save__move_branch_right(self):
        self.assertEqual(self.pages['Homepage'].left, 1)
        self.assertEqual(self.pages['Homepage'].right, 20)
        self.assertEqual(self.pages['Tree_1___Page_1'].left, 2)
        self.assertEqual(self.pages['Tree_1___Page_1'].right, 7)
        self.assertEqual(self.pages['Tree_1___Page_2'].left, 3)
        self.assertEqual(self.pages['Tree_1___Page_2'].right, 4)
        self.assertEqual(self.pages['Tree_1___Page_3'].left, 5)
        self.assertEqual(self.pages['Tree_1___Page_3'].right, 6)
        self.assertEqual(self.pages['Tree_2___Page_1'].left, 8)
        self.assertEqual(self.pages['Tree_2___Page_1'].right, 9)
        self.assertEqual(self.pages['Tree_3___Page_1'].left, 10)
        self.assertEqual(self.pages['Tree_3___Page_1'].right, 19)
        self.assertEqual(self.pages['Tree_3___Page_2'].left, 11)
        self.assertEqual(self.pages['Tree_3___Page_2'].right, 16)
        self.assertEqual(self.pages['Tree_3___Page_3'].left, 17)
        self.assertEqual(self.pages['Tree_3___Page_3'].right, 18)
        self.assertEqual(self.pages['Tree_3___Page_4'].left, 12)
        self.assertEqual(self.pages['Tree_3___Page_4'].right, 13)
        self.assertEqual(self.pages['Tree_3___Page_5'].left, 14)
        self.assertEqual(self.pages['Tree_3___Page_5'].right, 15)

        self.pages['Tree_1___Page_1'].parent = self.pages['Tree_3___Page_1']
        self.pages['Tree_1___Page_1'].save()

        # Rebuild page dict.
        self._rebuild_page_dict()

        self.assertEqual(self.pages['Homepage'].left, 1)
        self.assertEqual(self.pages['Homepage'].right, 20)
        self.assertEqual(self.pages['Tree_1___Page_1'].left, 13)
        self.assertEqual(self.pages['Tree_1___Page_1'].right, 18)
        self.assertEqual(self.pages['Tree_1___Page_2'].left, 14)
        self.assertEqual(self.pages['Tree_1___Page_2'].right, 15)
        self.assertEqual(self.pages['Tree_1___Page_3'].left, 16)
        self.assertEqual(self.pages['Tree_1___Page_3'].right, 17)
        self.assertEqual(self.pages['Tree_2___Page_1'].left, 2)
        self.assertEqual(self.pages['Tree_2___Page_1'].right, 3)
        self.assertEqual(self.pages['Tree_3___Page_1'].left, 4)
        self.assertEqual(self.pages['Tree_3___Page_1'].right, 19)
        self.assertEqual(self.pages['Tree_3___Page_2'].left, 5)
        self.assertEqual(self.pages['Tree_3___Page_2'].right, 10)
        self.assertEqual(self.pages['Tree_3___Page_3'].left, 11)
        self.assertEqual(self.pages['Tree_3___Page_3'].right, 12)
        self.assertEqual(self.pages['Tree_3___Page_4'].left, 6)
        self.assertEqual(self.pages['Tree_3___Page_4'].right, 7)
        self.assertEqual(self.pages['Tree_3___Page_5'].left, 8)
        self.assertEqual(self.pages['Tree_3___Page_5'].right, 9)

    def test_page_delete(self):
        self.pages['Tree_3___Page_5'].content.delete()
        self.pages['Tree_3___Page_5'].delete()

        # Rebuild page dict.
        self._rebuild_page_dict()

        self.assertEqual(self.pages['Homepage'].left, 1)
        self.assertEqual(self.pages['Homepage'].right, 18)
        self.assertEqual(self.pages['Tree_1___Page_1'].left, 2)
        self.assertEqual(self.pages['Tree_1___Page_1'].right, 7)
        self.assertEqual(self.pages['Tree_1___Page_2'].left, 3)
        self.assertEqual(self.pages['Tree_1___Page_2'].right, 4)
        self.assertEqual(self.pages['Tree_1___Page_3'].left, 5)
        self.assertEqual(self.pages['Tree_1___Page_3'].right, 6)
        self.assertEqual(self.pages['Tree_2___Page_1'].left, 8)
        self.assertEqual(self.pages['Tree_2___Page_1'].right, 9)
        self.assertEqual(self.pages['Tree_3___Page_1'].left, 10)
        self.assertEqual(self.pages['Tree_3___Page_1'].right, 17)
        self.assertEqual(self.pages['Tree_3___Page_2'].left, 11)
        self.assertEqual(self.pages['Tree_3___Page_2'].right, 14)
        self.assertEqual(self.pages['Tree_3___Page_3'].left, 15)
        self.assertEqual(self.pages['Tree_3___Page_3'].right, 16)
        self.assertEqual(self.pages['Tree_3___Page_4'].left, 12)
        self.assertEqual(self.pages['Tree_3___Page_4'].right, 13)

        with self.assertRaises(KeyError):
            self.pages['Tree_3___Page_5']
