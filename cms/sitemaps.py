'''Google sitemaps used by the page management application.'''

from django.contrib.sitemaps import Sitemap

# A dictionary of registered sitemap classes.
registered_sitemaps = {}


class BaseSitemap(Sitemap):

    '''
    Base sitemap for registration.

    Subclasses need to override the model property.
    '''

    model = None

    def items(self):
        '''Returns all items in this sitemap.'''
        return self.model.objects.all()


class PublishedBaseSitemap(BaseSitemap):

    '''Base sitemap for all subclasses of PublishedBase.'''


class OnlineBaseSitemap(PublishedBaseSitemap):

    '''Base sitemap for all subclasses of OnlineBase.'''


class SearchMetaBaseSitemap(OnlineBaseSitemap):

    '''Base sitemap for all subclasses of SearchMetaBase.'''

    def items(self):
        '''Only lists items that are marked as indexable.'''
        return super().items().filter(robots_index=True)

    def changefreq(self, obj):
        '''Returns the change frequency of the given page.'''
        if obj.sitemap_changefreq:
            return obj.get_sitemap_changefreq_display().lower()
        return None

    def priority(self, obj):
        '''Returns the priority of the given page.'''
        return obj.sitemap_priority


class PageBaseSitemap(SearchMetaBaseSitemap):

    '''
    Base sitemap for all subclasses of PageBase.

    Subclasses need to override the model property.
    '''


class SitemapRegistrationError(Exception):

    '''Error raised when a sitemap could not be registered.'''


def register(model, sitemap_cls=None):
    '''Registers a model with the sitemap registry.'''

    # These imports need to be here to avoid raising an exception when models
    # are registered in the module containing an AppConfig.
    from cms.models import OnlineBase, PageBase, PublishedBase, SearchMetaBase

    # Generate the registration key.
    registration_key = '{app_label}-{model_name}'.format(
        app_label=model._meta.app_label,
        model_name=model.__name__.lower(),
    )
    if registration_key in registered_sitemaps:
        raise SitemapRegistrationError('A sitemap has already been registered under {registration_key}'.format(
            registration_key=registration_key,
        ))
    # Generate the sitemap class.
    if not sitemap_cls:
        sitemap_classes = [
            (PageBase, PageBaseSitemap),
            (SearchMetaBase, SearchMetaBaseSitemap),
            (OnlineBase, OnlineBaseSitemap),
            (PublishedBase, PublishedBaseSitemap),
        ]

        sitemap_cls_base = BaseSitemap

        for model_base, map_class in sitemap_classes:
            if issubclass(model, model_base):
                sitemap_cls_base = map_class
                break

        sitemap_cls_name = model.__name__ + 'Sitemap'
        sitemap_cls = type(sitemap_cls_name, (sitemap_cls_base,), {
            'model': model,
        })
    # Register the sitemap.
    registered_sitemaps[registration_key] = sitemap_cls
