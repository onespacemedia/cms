from django.contrib.contenttypes.models import ContentType
from django.urls import resolve, is_valid_path, Resolver404
from django.conf import settings
from django.shortcuts import redirect
from django.http import Http404
from django.views.generic import TemplateView, View


class PageDispatcherView(View):
    def dispatch(self, request, *args, **kwargs):
        # Get the current page.
        page = request.pages.current

        if page is None:
            raise Http404('There is no homepage for this site or it is set to offline.')

        # Dispatch to the content.
        try:
            callback, callback_args, callback_kwargs = resolve(request.pages.current_path, page.content.urlconf)

            response = callback(request, *callback_args, **callback_kwargs)

        except Resolver404:
            raise Http404(f'No page or matching URL pattern found for "{request.pages.current_path[1:]}"')

        if page.auth_required() and not request.user.is_authenticated:
            return redirect('{}?next={}'.format(
                settings.LOGIN_URL,
                request.path
            ))

        return response


class ContentIndexView(TemplateView):

    '''Displays the index page for a page.'''

    def get_template_names(self):
        '''
        Returns the list of template names, guessing an appropriate name for
        the content type. For a hypothetical "example" app with a "Content"
        model, it will look for them in this order:

        example/content.html
        example/base.html
        base.html
        '''
        content_cls = ContentType.objects.get_for_id(self.request.pages.current.content_type_id).model_class()
        params = {
            'model_name': content_cls.__name__.lower(),
            'app_label': content_cls._meta.app_label,
        }
        return (
            '{app_label}/{model_name}.html'.format(**params),
            '{app_label}/base.html'.format(**params),
            'base.html',
        )
