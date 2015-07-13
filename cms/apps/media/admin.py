"""Admin settings for the static media management application."""

import os
from functools import partial

from django.core.files import File as DjangoFile
from django.core.files.temp import NamedTemporaryFile
from django.core.paginator import Paginator
from django.conf.urls import patterns, url
from django.contrib import admin, messages
from django.contrib.admin.views.main import IS_POPUP_VAR
from django.contrib.staticfiles.storage import staticfiles_storage
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotAllowed, Http404
from django.shortcuts import render, get_object_or_404
from django.template.defaultfilters import filesizeformat
from django.utils.text import Truncator

from sorl.thumbnail import get_thumbnail
from cms import permalinks, externals
from cms.apps.media.models import Label, File, Video

import requests
import json


class LabelAdmin(admin.ModelAdmin):

    """Admin settings for Label models."""

    list_display = ("name",)

    search_fields = ("name",)


admin.site.register(Label, LabelAdmin)


class VideoAdmin(admin.ModelAdmin):

    def to_field_allowed(self, request, to_field):
        """
        This is a workaround for issue #552 which will raise a security
        exception in the media select popup with django 1.6.6.
        According to the release notes, this should be fixed by the
        yet (2014-09-22) unreleased 1.6.8, 1.5.11, 1.7.1.

        Details: https://code.djangoproject.com/ticket/23329#comment:11
        """

        if to_field == 'id':
            return True

        return super(VideoAdmin, self).to_field_allowed(request, to_field)

admin.site.register(Video, VideoAdmin)


# Different types of file.
AUDIO_FILE_ICON = "media/img/audio-x-generic.png"
DOCUMENT_FILE_ICON = "media/img/x-office-document.png"
SPREADSHEET_FILE_ICON = "media/img/x-office-spreadsheet.png"
TEXT_FILE_ICON = "media/img/text-x-generic.png"
IMAGE_FILE_ICON = "media/img/image-x-generic.png"
MOVIE_FILE_ICON = "media/img/video-x-generic.png"
UNKNOWN_FILE_ICON = "media/img/text-x-generic-template.png"

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
    'webm': MOVIE_FILE_ICON,
    'm4v': MOVIE_FILE_ICON,
}


class FileAdminBase(admin.ModelAdmin):

    """Admin settings for File models."""

    fieldsets = (
        (None, {
            "fields": ("title", "file",),
        },),
        ("Media management", {
            "fields": ("attribution", "copyright", "labels",),
        },),
    )

    list_filter = ("labels",)

    search_fields = ("title",)

    list_display = ("get_preview", "get_title", "get_size",)

    change_list_template = "admin/media/file/change_list.html"

    filter_horizontal = ("labels",)

    def to_field_allowed(self, request, to_field):
        """
        This is a workaround for issue #552 which will raise a security
        exception in the media select popup with django 1.6.6.
        According to the release notes, this should be fixed by the
        yet (2014-09-22) unreleased 1.6.8, 1.5.11, 1.7.1.

        Details: https://code.djangoproject.com/ticket/23329#comment:11
        """

        if to_field == 'id':
            return True

        return super(FileAdminBase, self).to_field_allowed(request, to_field)

    # Custom actions.

    def add_label_action(self, request, queryset, label):
        """Adds the label on the given queryset."""
        for file in queryset:
            file.labels.add(label)

    def remove_label_action(self, request, queryset, label):
        """Removes the label on the given queryset."""
        for file in queryset:
            file.labels.remove(label)

    def get_actions(self, request):
        """Generates the actions for assigning categories."""
        if IS_POPUP_VAR in request.GET:
            return []
        opts = self.model._meta
        verbose_name_plural = opts.verbose_name_plural
        actions = super(FileAdminBase, self).get_actions(request)
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
                pass
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
                    pass
        else:
            icon = staticfiles_storage.url(icon)

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
    get_title.short_description = "title"

    # Custom view logic.

    def response_add(self, request, obj, *args, **kwargs):
        """Returns the response for a successful add action."""
        if "_redactor" in request.GET:
            context = {"permalink": permalinks.create(obj),
                       "title": obj.title}
            return render(request, "admin/media/file/filebrowser_add_success.html", context)
        return super(FileAdminBase, self).response_add(request, obj, *args, **kwargs)

    def changelist_view(self, request, extra_context=None):
        """Renders the change list."""
        context = {
            "changelist_template_parent": externals.reversion and "reversion/change_list.html" or "admin/change_list.html",
        }
        if extra_context:
            context.update(extra_context)
        return super(FileAdminBase, self).changelist_view(request, context)

    # Create a URL route and a view for saving the Adobe SDK callback URL.
    def get_urls(self):
        urls = super(FileAdminBase, self).get_urls()

        new_urls = patterns(
            '',
            url(r'^(?P<object_id>\d+)/remote/$', self.remote_view, name="media_file_remote"),

            url(r'^redactor/upload/(?P<file_type>image|file)/$', self.redactor_upload, name="media_file_redactor_upload"),

            url(r'^redactor/(?P<file_type>images|files)/$', self.redactor_data, name="media_file_redactor_data"),
            url(r'^redactor/(?P<file_type>images|files)/(?P<page>\d+)/$', self.redactor_data, name="media_file_redactor_data"),
        )

        return new_urls + urls

    def remote_view(self, request, object_id):
        if not self.has_change_permission(request):
            return HttpResponseForbidden("You do not have permission to modify this file.")

        if request.method != 'POST':
            return HttpResponseNotAllowed(['POST'])

        url = request.POST.get('url', None)

        if not url:
            raise Http404("No URL supplied.")

        # Pull down the remote image and save it as a temporary file.
        img_temp = NamedTemporaryFile()
        img_temp.write(requests.get(url).content)
        img_temp.flush()

        obj = get_object_or_404(File, pk=object_id)
        obj.file.save(url.split('/')[-1], DjangoFile(img_temp))

        messages.success(request, 'The file "{}" was changed successfully. You may edit it again below.'.format(
            obj.__str__()
        ))
        return HttpResponse('{"status": "ok"}', content_type='application/json')

    def redactor_data(self, request, **kwargs):
        if not self.has_change_permission(request):
            return HttpResponseForbidden("You do not have permission to view these files.")

        file_type = kwargs.get('file_type', 'files')
        page = kwargs.get('page', 1)

        # Make sure we serve the correct data
        if file_type == 'files':
            file_objects = File.objects.all()
        elif file_type == 'images':
            file_objects = File.objects.filter(file__regex=r'(?i)\.(png|gif|jpg|jpeg)$')

        # Sort objects by title
        file_objects = file_objects.order_by('title')

        # Create paginator
        paginator = Paginator(file_objects, 15)

        # Create files usable by the CMS
        json_data = {
            'page': page,
            'pages': paginator.page_range,
        }

        if file_type == 'files':
            json_data['objects'] = [
                {'title': file_object.title, 'url': permalinks.create(file_object)}
                for file_object in paginator.page(page)
            ]
        elif file_type == 'images':
            json_data['objects'] = [
                {'title': file_object.title, 'url': permalinks.create(file_object), 'thumbnail': get_thumbnail(file_object.file, '100x75', crop="center", quality=99).url}
                for file_object in paginator.page(page)
            ]

        # Return files as ajax
        return HttpResponse(json.dumps(json_data), content_type='application/json')

    def redactor_upload(self, request, file_type):
        if not self.has_change_permission(request):
            return HttpResponseForbidden("You do not have permission to upload this file.")

        if request.method != 'POST':
            return HttpResponseNotAllowed(['POST'])

        image_content_types = [
            'image/gif',
            'image/jpeg',
            'image/png',
            'image/bmp'
        ]

        try:

            if file_type == 'image':
                if request.FILES.getlist('file')[0].content_type not in image_content_types:
                    raise Exception()

            new_file = File(
                title=request.FILES.getlist('file')[0].name,
                file=request.FILES.getlist('file')[0]
            )
            new_file.save()

            if file_type == 'image':
                return HttpResponse(json.dumps({
                    'filelink': permalinks.create(new_file)
                }))
            else:
                return HttpResponse(json.dumps({
                    'filelink': permalinks.create(new_file),
                    'filename': request.FILES.getlist('file')[0].name,
                }))

        except:
            return HttpResponse('')


# Renaming needed to allow inheritance to take place in this class without infinite recursion.
FileAdmin = FileAdminBase


if externals.reversion:
    class FileAdmin(FileAdmin, externals.reversion["admin.VersionMetaAdmin"]):
        list_display = FileAdmin.list_display + ("get_date_modified",)


if externals.watson:
    class FileAdmin(FileAdmin, externals.watson["admin.SearchAdmin"]):
        pass


admin.site.register(File, FileAdmin)
