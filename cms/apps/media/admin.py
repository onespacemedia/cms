"""Admin settings for the static media management application."""
from __future__ import unicode_literals

import os
from functools import partial

import requests
from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.views.main import IS_POPUP_VAR
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.files import File as DjangoFile
from django.core.files.temp import NamedTemporaryFile
from django.http import (Http404, HttpResponse, HttpResponseForbidden,
                         HttpResponseNotAllowed)
from django.shortcuts import get_object_or_404, render
from django.template.defaultfilters import filesizeformat
from django.utils.text import Truncator
from reversion.admin import VersionAdmin
from sorl.thumbnail import get_thumbnail
from watson.admin import SearchAdmin

from cms import permalinks
from cms.apps.media.forms import ImageChangeForm
from cms.apps.media.models import File, Label, Video


class LabelAdmin(admin.ModelAdmin):
    """Admin settings for Label models."""

    list_display = ("name",)

    search_fields = ("name",)


admin.site.register(Label, LabelAdmin)


class VideoAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': ['title', 'image', 'high_resolution_mp4', 'low_resolution_mp4', 'external_video'],
        }),
    ]

admin.site.register(Video, VideoAdmin)

# Different types of file.
AUDIO_FILE_ICON = static("media/img/audio-x-generic.png")
DOCUMENT_FILE_ICON = static("media/img/x-office-document.png")
SPREADSHEET_FILE_ICON = static("media/img/x-office-spreadsheet.png")
TEXT_FILE_ICON = static("media/img/text-x-generic.png")
IMAGE_FILE_ICON = static("media/img/image-x-generic.png")
MOVIE_FILE_ICON = static("media/img/video-x-generic.png")
UNKNOWN_FILE_ICON = static("media/img/text-x-generic-template.png")

# Different types of recognised file extensions.
FILE_ICONS = {
    "mp3": AUDIO_FILE_ICON,
    "m4a": AUDIO_FILE_ICON,
    "wav": AUDIO_FILE_ICON,
    "doc": DOCUMENT_FILE_ICON,
    "odt": DOCUMENT_FILE_ICON,
    "pdf": DOCUMENT_FILE_ICON,
    "xls": SPREADSHEET_FILE_ICON,
    "txt": TEXT_FILE_ICON,
    "png": IMAGE_FILE_ICON,
    "gif": IMAGE_FILE_ICON,
    "jpg": IMAGE_FILE_ICON,
    "jpeg": IMAGE_FILE_ICON,
    "swf": MOVIE_FILE_ICON,
    "flv": MOVIE_FILE_ICON,
    "mp4": MOVIE_FILE_ICON,
    "mov": MOVIE_FILE_ICON,
    "wmv": MOVIE_FILE_ICON,
    'm4v': MOVIE_FILE_ICON,
}


class FileAdmin(VersionAdmin, SearchAdmin):
    """Admin settings for File models."""

    change_list_template = 'admin/media/file/change_list.html'
    fieldsets = [
        (None, {
            'fields': ["title", "file"],
        }),
        ('Media management', {
            'fields': ['attribution', 'copyright', 'alt_text', 'labels'],
        }),
    ]
    filter_horizontal = ['labels']
    list_display = ['get_preview', 'get_number', 'get_title', 'get_alt_text', 'get_size']
    list_display_links = list_display
    list_filter = ['labels']
    search_fields = ['title']
    ordering = ['pk']

    def get_form(self, request, obj=None, **kwargs):
        if obj and obj.is_image:
            kwargs['form'] = ImageChangeForm
        return super(FileAdmin, self).get_form(request, obj, **kwargs)

    def get_number(self, obj):
        return obj.pk

    get_number.admin_order_field = 'pk'
    get_number.short_description = "number"

    def get_alt_text(self, obj):
        if not obj.alt_text:
            return ''

        return obj.alt_text

    get_alt_text.short_description = "Alt text"

    # Custom actions.

    def add_label_action(self, request, queryset, label):
        """Adds the label on the given queryset."""
        for obj in queryset:
            obj.labels.add(label)

    def remove_label_action(self, request, queryset, label):
        """Removes the label on the given queryset."""
        for obj in queryset:
            obj.labels.remove(label)

    def get_actions(self, request):
        """Generates the actions for assigning categories."""
        if IS_POPUP_VAR in request.GET:
            return []
        opts = self.model._meta
        verbose_name_plural = opts.verbose_name_plural
        actions = super(FileAdmin, self).get_actions(request)
        # Add the dynamic labels.
        for label in Label.objects.all():
            # Add action.
            action_function = partial(self.__class__.add_label_action, label=label)
            action_description = 'Remove label %s from selected %s"' % (label.name, verbose_name_plural)
            action_name = action_description.lower().replace(" ", "_")
            actions[action_name] = (action_function, action_name, action_description)
            # Remove action.
            action_function = partial(self.__class__.remove_label_action, label=label)
            action_description = 'Remove label %s from selected %s"' % (label.name, verbose_name_plural)
            action_name = action_description.lower().replace(" ", "_")
            actions[action_name] = (action_function, action_name, action_description)
        return actions

    # Custom display routines.
    def get_size(self, obj):
        """Returns the size of the media in a human-readable format."""
        try:
            return filesizeformat(obj.file.size)
        except OSError:
            return "0 bytes"

    get_size.short_description = "size"

    def get_preview(self, obj):
        """Generates a thumbnail of the image."""
        _, extension = os.path.splitext(obj.file.name)
        extension = extension.lower()[1:]
        icon = FILE_ICONS.get(extension, UNKNOWN_FILE_ICON)
        permalink = permalinks.create(obj)
        if icon == IMAGE_FILE_ICON:
            try:
                thumbnail = get_thumbnail(obj.file, '100x66', quality=99)
            except IOError:
                return '<img cms:permalink="{}" src="{}" width="66" height="66" alt="" title="{}"/>'.format(
                    permalink,
                    icon,
                    obj.title
                )
            else:
                try:
                    return '<img cms:permalink="{}" src="{}" width="{}" height="{}" alt="" title="{}"/>'.format(
                        permalink,
                        thumbnail.url,
                        thumbnail.width,
                        thumbnail.height,
                        obj.title
                    )
                except TypeError:
                    return '<img cms:permalink="{}" src="{}" width="66" height="66" alt="" title="{}"/>'.format(
                        permalink,
                        icon,
                        obj.title
                    )

        return '<img cms:permalink="{}" src="{}" width="66" height="66" alt="" title="{}"/>'.format(
            permalink,
            icon,
            obj.title
        )

    get_preview.short_description = "preview"
    get_preview.allow_tags = True

    def get_title(self, obj):
        """Returns a truncated title of the object."""
        return Truncator(obj.title).words(8)
    get_title.admin_order_field = 'title'
    get_title.short_description = "title"

    # Custom view logic.

    def response_add(self, request, obj, post_url_continue=None):
        """Returns the response for a successful add action."""
        if "_tinymce" in request.GET:
            context = {"permalink": permalinks.create(obj),
                       "title": obj.title}
            return render(request, "admin/media/file/filebrowser_add_success.html", context)
        return super(FileAdmin, self).response_add(request, obj, post_url_continue=post_url_continue)

    def changelist_view(self, request, extra_context=None):
        """Renders the change list."""
        context = extra_context or {}

        if not 'changelist_template_parent' in context:
            context['changelist_template_parent'] = 'reversion/change_list.html'

        return super(FileAdmin, self).changelist_view(request, context)

    def media_library_changelist_view(self, request, extra_context=None):
        '''Renders the change list, but sets 'is_popup=True' into the template
        context to make it render the media library sans navigation, without
        needing _popup in the URL (which causes an exception with Jet's
        Javascript, which assumes that if _popup is in the URL that it is a
        related item popup).'''
        context = extra_context or {}

        if not 'changelist_template_parent' in context:
            context['changelist_template_parent'] = 'reversion/change_list.html'

        context['is_popup'] = True
        context['is_media_library_iframe'] = True

        return super(FileAdmin, self).changelist_view(request, context)

    # Create a URL route and a view for saving the Adobe SDK callback URL.
    def get_urls(self):
        urls = super(FileAdmin, self).get_urls()

        new_urls = [
            url(r'^(?P<object_id>\d+)/remote/$', self.remote_view, name="media_file_remote"),
            url(r'^media-library-wysiwyg/$', self.media_library_changelist_view, name='media_file_wysiwyg_list'),
        ]

        return new_urls + urls

    def remote_view(self, request, object_id):
        if not self.has_change_permission(request):
            return HttpResponseForbidden("You do not have permission to modify this file.")

        if request.method != 'POST':
            return HttpResponseNotAllowed(['POST'])

        image_url = request.POST.get('url', None)

        if not image_url:
            raise Http404("No URL supplied.")

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


admin.site.register(File, FileAdmin)
