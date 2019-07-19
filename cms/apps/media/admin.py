'''Admin settings for the static media management application.'''
from functools import partial

import requests
from cms import permalinks
from cms.apps.media.forms import FileForm, ImageChangeForm
from cms.apps.media.models import File, Label, Video
from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.views.main import IS_POPUP_VAR
from django.core.files import File as DjangoFile
from django.core.files.temp import NamedTemporaryFile
from django.core.urlresolvers import reverse
from django.db.models.deletion import get_candidate_relations_to_delete
from django.db.utils import DEFAULT_DB_ALIAS
from django.http import (Http404, HttpResponse, HttpResponseForbidden,
                         HttpResponseNotAllowed)
from django.shortcuts import get_object_or_404, render
from django.template.defaultfilters import filesizeformat
from django.utils.html import format_html
from django.utils.text import Truncator
from reversion.admin import VersionAdmin
from sorl.thumbnail import get_thumbnail
from watson.admin import SearchAdmin


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    '''Admin settings for Label models.'''

    list_display = ('name',)

    search_fields = ('name',)


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': ['title', 'image', 'high_resolution_mp4', 'low_resolution_mp4', 'external_video'],
        }),
    ]


@admin.register(File)
class FileAdmin(VersionAdmin, SearchAdmin):
    '''Admin settings for File models.'''

    change_list_template = 'admin/media/file/change_list.html'
    fieldsets = [
        (None, {
            'fields': ['title', 'file'],
        }),
        ('Media management', {
            'fields': ['attribution', 'copyright', 'alt_text', 'labels'],
        }),
    ]
    filter_horizontal = ['labels']
    list_display = ['get_number', 'get_preview', 'get_title', 'get_alt_text', 'get_size']
    list_display_links = list_display
    list_filter = ['labels']
    search_fields = ['title']

    def get_form(self, request, obj=None, **kwargs):
        if obj and obj.is_image():
            kwargs['form'] = ImageChangeForm
        else:
            kwargs['form'] = FileForm
        return super().get_form(request, obj, **kwargs)

    def get_number(self, obj):
        return obj.pk

    get_number.admin_order_field = 'pk'
    get_number.short_description = 'number'

    def get_alt_text(self, obj):
        if not obj.alt_text:
            return ''

        return obj.alt_text

    get_alt_text.short_description = 'Alt text'

    # Custom actions.

    def add_label_action(self, request, queryset, label):
        '''Adds the label on the given queryset.'''
        for obj in queryset:
            obj.labels.add(label)

    def remove_label_action(self, request, queryset, label):
        '''Removes the label on the given queryset.'''
        for obj in queryset:
            obj.labels.remove(label)

    def get_actions(self, request):
        '''Generates the actions for assigning categories.'''
        if IS_POPUP_VAR in request.GET:
            return []
        opts = self.model._meta
        verbose_name_plural = opts.verbose_name_plural
        actions = super().get_actions(request)
        # Add the dynamic labels.
        for label in Label.objects.all():
            # Add action.
            action_function = partial(self.__class__.add_label_action, label=label)
            action_description = 'Remove label %s from selected %s' % (label.name, verbose_name_plural)
            action_name = action_description.lower().replace(' ', '_')
            actions[action_name] = (action_function, action_name, action_description)
            # Remove action.
            action_function = partial(self.__class__.remove_label_action, label=label)
            action_description = 'Remove label %s from selected %s' % (label.name, verbose_name_plural)
            action_name = action_description.lower().replace(' ', '_')
            actions[action_name] = (action_function, action_name, action_description)
        return actions

    # Custom display routines.
    def get_size(self, obj):
        '''Returns the size of the media in a human-readable format.'''
        try:
            return filesizeformat(obj.file.size)
        except OSError:
            return '0 bytes'

    get_size.short_description = 'size'

    def get_preview(self, obj):
        '''Generates a thumbnail of the image, falling back to an appropriate
        icon if it is not an image file or if thumbnailing fails.'''
        icon = obj.icon
        permalink = permalinks.create(obj)
        if obj.is_image():
            try:
                thumbnail = get_thumbnail(obj.file, '100x66', quality=99)
                return format_html(
                    '<img cms:permalink="{}" src="{}" width="{}" height="{}" alt="" title="{}"/>',
                    permalink,
                    thumbnail.url,
                    thumbnail.width,
                    thumbnail.height,
                    obj.title
                )

            # AttributeError will be raised if thumbnail returns None - the
            # others can be raised with bad files.
            except (IOError, TypeError, AttributeError):
                pass

        return format_html(
            '<img cms:permalink="{}" src="{}" width="56" height="66" alt="" title="{}"/>',
            permalink,
            icon,
            obj.title
        )
    get_preview.short_description = 'preview'

    def get_title(self, obj):
        '''Returns a truncated title of the object.'''
        return Truncator(obj.title).words(8)
    get_title.admin_order_field = 'title'
    get_title.short_description = 'title'

    def get_related_pages(self, querysets):
        pages = []
        for queryset in querysets:
            for model in queryset:
                if hasattr(model, 'page'):
                    pages.append(model)
                else:
                    pages.append(model.__class__.objects.get(pk=model.id))

        return pages

    def get_admin_url(self, model):
        model_name = model.__class__.__name__

        model_admin_urls = {
            'Article':
                {
                    'url': 'admin:news_article_change',
                    'args': [model.pk],
                },
            'CallToAction':
                {
                    'url': 'admin:components_calltoaction_change',
                    'args': [model.pk],
                },
            'Career':
                {
                    'url': 'admin:careers_career_change',
                    'args': [model.pk],
                },
            'Client': {
                'url': 'admin:projects_client_change',
                'args': [model.pk],
            },
            'ContentSection': {
                'url': 'admin:pages_page_change',
                'args': [model.page.pk] if hasattr(model, 'page') else [],
            },
            'Event': {
                'url': 'admin:events_event_change',
                'args': [model.pk],
            },
            'Footer': {
                'url': 'admin:site_footer_change',
                'args': [model.pk],
            },
            'Logo': {
                'url': 'admin:components_logoset_change',
                'args': [model.set.pk] if hasattr(model, 'set') else [],
            },
            'Office': {
                'url': 'admin:contact_office_change',
                'args': [model.pk],
            },
            'Page':
                {
                    'url': 'admin:pages_page_change',
                    'args': [model.pk],
                },
            'Person': {
                'url': 'admin:people_person_change',
                'args': [model.pk],
            },
            'Project': {
                'url': 'admin:projects_project_change',
                'args': [model.pk],
            },
            'Sector': {
                'url': 'admin:sectors_sector_change',
                'args': [model.pk],
            },
        }


        if model_name in model_admin_urls:
            model = model_admin_urls.get(model_name)
            model_url = model.get('url')
            model_args = model.get('args')

            return reverse(model_url, args=model_args)


    # Custom view logic.

    def response_add(self, request, obj, post_url_continue=None):
        '''Returns the response for a successful add action.'''
        if '_tinymce' in request.GET:
            context = {'permalink': permalinks.create(obj),
                       'title': obj.title}
            return render(request, 'admin/media/file/filebrowser_add_success.html', context)
        return super().response_add(request, obj, post_url_continue=post_url_continue)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        # Strip all non-numeric characters from object_id to prevent an issue where object_id was returning a string (eg: '1231/change/none)
        object_id = ''.join(i for i in object_id if i.isdigit())
        test_obj = File.objects.get(pk=object_id)
        querysets = []

        for related in get_candidate_relations_to_delete(test_obj._meta):
            related_objs = related.related_model._base_manager.using(DEFAULT_DB_ALIAS).filter(
                **{"%s__in" % related.field.name: [test_obj]}
            )

            if related_objs:
                querysets.append(related_objs)

        extra_context['related_objects'] = [
            {
            'pages': [
                {
                    'page': page,
                    'model_name': page.__class__.__name__,
                    'admin_url': self.get_admin_url(page),
                } for page in self.get_related_pages(querysets)]
            }
        ]

        return super(FileAdmin, self).change_view(request, object_id, extra_context=extra_context)

    def changelist_view(self, request, extra_context=None):
        '''Renders the change list.'''
        context = extra_context or {}

        context.setdefault('changelist_template_parent', 'reversion/change_list.html')

        return super().changelist_view(request, context)

    def media_library_changelist_view(self, request, extra_context=None):
        '''Renders the change list, but sets 'is_popup=True' into the template
        context to make it render the media library sans navigation, without
        needing _popup in the URL (which causes an exception with Jet's
        Javascript, which assumes that if _popup is in the URL that it is a
        related item popup).'''
        context = extra_context or {}
        context.setdefault('changelist_template_parent', 'reversion/change_list.html')
        context['is_popup'] = True
        context['is_media_library_iframe'] = True

        return super().changelist_view(request, context)

    # Create a URL route and a view for saving the Adobe SDK callback URL.
    def get_urls(self):
        urls = super().get_urls()

        new_urls = [
            url(r'^(?P<object_id>\d+)/remote/$', self.remote_view, name='media_file_remote'),
            url(r'^media-library-wysiwyg/$', self.media_library_changelist_view, name='media_file_wysiwyg_list'),
        ]

        return new_urls + urls

    def remote_view(self, request, object_id):
        if not self.has_change_permission(request):
            return HttpResponseForbidden('You do not have permission to modify this file.')

        if request.method != 'POST':
            return HttpResponseNotAllowed(['POST'])

        image_url = request.POST.get('url', None)

        if not image_url:
            raise Http404('No URL supplied.')

        # Pull down the remote image and save it as a temporary file.
        img_temp = NamedTemporaryFile()
        img_temp.write(requests.get(image_url).content)
        img_temp.flush()

        obj = get_object_or_404(File, pk=object_id)
        obj.file.save(image_url.split('/')[-1], DjangoFile(img_temp))

        messages.success(request, 'The file "{}" was changed successfully. You may edit it again below.'.format(
            obj.__str__()
        ))
        return HttpResponse('{"status": "ok"}', content_type='application/json')
