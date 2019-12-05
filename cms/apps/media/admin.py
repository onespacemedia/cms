'''Admin settings for the static media management application.'''
from functools import partial

import requests

from django.apps import apps
from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.views.main import IS_POPUP_VAR
from django.core.files import File as DjangoFile
from django.core.files.temp import NamedTemporaryFile
from django.db.models.deletion import get_candidate_relations_to_delete
from django.db.utils import DEFAULT_DB_ALIAS
from django.http import (Http404, HttpResponse, HttpResponseForbidden,
                         HttpResponseNotAllowed)
from django.shortcuts import get_object_or_404, render
from django.template.defaultfilters import filesizeformat
from django.template.loader import render_to_string
from django.urls import NoReverseMatch, reverse
from django.utils.html import format_html
from django.utils.text import Truncator
from reversion.admin import VersionAdmin
from sorl.thumbnail import get_thumbnail
from watson.admin import SearchAdmin

from cms import permalinks
from cms.apps.media.forms import ImageChangeForm, FileForm
from cms.apps.media.models import File, Label, Video
from cms.apps.pages.admin import page_admin
from cms.apps.pages.models import Page
from cms.admin import get_related_objects_admin_urls


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
        ('Usage', {
            # This is the used_on function, not a field.
            'fields': ['used_on'],
        }),
    ]
    filter_horizontal = ['labels']
    list_display = ['get_number', 'get_preview', 'get_title', 'get_alt_text', 'get_size']
    list_display_links = list_display
    list_filter = ['labels']
    readonly_fields = ['used_on']
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

    def used_on(self, obj=None):
        context = {}

        if obj:
            context['related_objects'] = get_related_objects_admin_urls(obj)
        else:
            context['related_objects'] = []
        return render_to_string('admin/media/includes/file_used_on.html', context)

    def response_add(self, request, obj, post_url_continue=None):
        '''Returns the response for a successful add action.'''
        if '_tinymce' in request.GET:
            context = {'permalink': permalinks.create(obj),
                       'title': obj.title}
            return render(request, 'admin/media/file/filebrowser_add_success.html', context)
        return super().response_add(request, obj, post_url_continue=post_url_continue)

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
