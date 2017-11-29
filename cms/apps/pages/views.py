from cms.apps.pages.models import Page
from django.contrib.auth.views import redirect_to_login
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.template.response import TemplateResponse
from django.urls import resolve
from django.views.generic import TemplateView


class ContentIndexView(TemplateView):

    """Displays the index page for a page."""

    def get_template_names(self):
        """Returns the list of template names."""
        content_cls = ContentType.objects.get_for_id(self.request.pages.current.content_type_id).model_class()
        params = {
            "model_name": content_cls.__name__.lower(),
            "app_label": content_cls._meta.app_label,
        }
        return (
            "{app_label}/{model_name}.html".format(**params),
            "{app_label}/base.html".format(**params),
            "base.html",
        )


class Struct(object):
    def __init__(self, **entries):
        self.__dict__.update(entries)


def get_page(page, breadcrumbs, path_components):
    content_cls = ContentType.objects.get_for_id(page.content_type_id).model_class()

    if path_components:
        child_slug = path_components[0]
        remaining_components = path_components[1:]

        try:
            subpage = page.child_set.get(slug=child_slug)
        except Page.DoesNotExist:
            if content_cls.urlconf == 'cms.apps.pages.urls':
                raise Http404

            return page, path_components

        breadcrumbs.append(subpage)
        return get_page(subpage, breadcrumbs, remaining_components)

    return page, path_components


def page_detail(request, path):
    path_components = [component for component in path.split('/') if component]
    homepage = Page.objects.get(parent=None)
    breadcrumbs = [homepage]

    page, path_components = get_page(homepage, breadcrumbs, path_components)
    content_cls = ContentType.objects.get_for_id(page.content_type_id).model_class()

    # Try to resolve the page using the ContentBase urlconf
    try:
        func, args, kwargs = resolve('/{}'.format('/'.join(path_components)), content_cls.urlconf)
    except Http404:
        func, args, kwargs = resolve('/{}/'.format('/'.join(path_components)), content_cls.urlconf)

    request.pages = Struct(**{
        'current': page,
        'homepage': homepage,
        'breadcrumbs': breadcrumbs,
    })

    if page.auth_required() and not request.user.is_authenticated():
        return redirect_to_login(path)

    return func(request, *args, **kwargs)
