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


PAGE_FIELDS = ['id', 'title', 'content_type_id', 'requires_authentication']


def get_page(page, breadcrumbs, path_components, auth_required):
    content_cls = ContentType.objects.get_for_id(page.content_type_id).model_class()

    if path_components:
        child_slug = path_components[0]
        remaining_components = path_components[1:]

        try:
            subpage = page.children.only(*PAGE_FIELDS).get(slug=child_slug)
        except Page.DoesNotExist:
            if content_cls.urlconf == 'cms.apps.pages.urls':
                raise Http404

            return page, path_components, auth_required

        breadcrumbs.append(subpage)

        auth_required = not auth_required and subpage.auth_required
        return get_page(subpage, breadcrumbs, remaining_components, auth_required)

    return page, path_components, auth_required


def page_detail(request, path):
    path_components = [component for component in path.split('/') if component]
    homepage = Page.objects.get_homepage()
    breadcrumbs = [homepage]

    page, path_components, auth_required = get_page(homepage, breadcrumbs, path_components, homepage.requires_authentication)
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

    if auth_required and not request.user.is_authenticated:
        return redirect_to_login(path)

    return func(request, *args, **kwargs)
