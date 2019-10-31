'''Admin settings for the static media management application.'''
from functools import partial

import requests

from django.apps import apps
from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.views.main import IS_POPUP_VAR
from django.core.files import File as DjangoFile
from django.core.files.temp import NamedTemporaryFile
from django.core.urlresolvers import NoReverseMatch, reverse
from django.db.models.deletion import get_candidate_relations_to_delete
from django.db.utils import DEFAULT_DB_ALIAS
from django.http import (Http404, HttpResponse, HttpResponseForbidden,
                         HttpResponseNotAllowed)
from django.shortcuts import get_object_or_404, render
from django.template.defaultfilters import filesizeformat
from django.template.loader import render_to_string
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

    def check_inline_for_admin_url(self, obj, inline, parent):
        '''
        A function used to get the admin URL for an obj.

        Takes the object itself, an inline object and the class of the
        parent model.

        If no change URL is found, None is returned.
        '''
        # We obviously need the object to be the same type of object
        # as the inline to at least get anywhere useful. We catch this
        # straight away and immediately return if so to save time.
        if not isinstance(obj, inline.model):
            return None

        # We've got an inline for this model. Lets check the fk_name
        # attribute on the InlineModelAdmin. If it's set we'll use
        # that, else we'll find the ForeignKey to the parent.

        obj_fk_name = getattr(inline, 'fk_name', False)
        if obj_fk_name:
            # the fk_name value is set so we assume that it will
            # resolve a parent since an inline can't be saved without
            # a parent.

            obj_parent = getattr(obj, obj_fk_name, False)
            try:
                return reverse(
                    f'admin:{obj_parent._meta.app_label}_{obj_parent._meta.model_name}_change',
                    args=[obj_parent.pk]
                )
            except NoReverseMatch:
                pass

        # If we make it here, the fk_name attribute was not set or the
        # parent did not resolve to an object We'll now look for
        # specifically ForeignKeys to the parent model. There can't be
        # more than one as if there were, Django would throw errors on
        # inline registration due to the lack of the fk_name
        # attribute to distinguish the two fields.

        for field in obj._meta.get_fields():
            if field.get_internal_type() in ['ForeignKey']:
                # Follow the ForeignKey to find the related model.

                related_model = obj._meta.get_field(field.attname).rel.to

                if parent == related_model:
                    # We've found a Foreign key to the parent, now
                    # to extract the page and get its admin change URL.

                    try:
                        field_value = getattr(obj, field.attname)
                    except AttributeError:
                        field_value = None

                    if field_value:
                        try:
                            return reverse(
                                f'admin:{related_model._meta.app_label}_{related_model._meta.model_name}_change',
                                args=[field_value]
                            )
                        except NoReverseMatch:
                            return None

    def get_admin_url(self, obj):
        '''
        Guesses the admin URL for an object.

        If the object has its own change view, then that will be returned.

        It will then check to see if it is an inline on another object's
        change view.

        Failing that, it will see if it is an inline registered to a Page
        (with page_admin.register_content_inline).
        '''
        # We first of all just ry and get an admin URL for the object that has
        # been passed to us.
        try:
            return reverse(
                f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change',
                args=[obj.pk]
            )
        except NoReverseMatch:
            pass

        # If we can't get and admin change URL for the object directly, we'll
        # now see if it's an inline with a parent model. If so, we'll return
        # the parent model's change URL
        # Having been given an arbitrary object, the only way we can work explicitly
        # out what the object's parent is, without making any assumptions, is by
        # looking through all registered models and tunneling down.

        for model, model_admin in admin.site._registry.items():
            # Check if the model we're looknig at has any inlines. If it hasn't had
            # any inlines set, model.inlines returns an empty array.
            inlines = model_admin.inlines

            # Loop over the model's inlines and check for references to our obj
            for inline in inlines:
                url = self.check_inline_for_admin_url(obj, inline, type(model))

                if url:
                    return url

        # If we've made it here, then obj is neither an object with an admin
        # change URL nor is it an inline of a registered model with an admin
        # change URL. Lets check inlines registered with page_admin.
        for _, inline in page_admin.content_inlines:
            # page_admin.content_inlines is a list of tuples. The first value
            # is the ContentType and the second is the inline InlineModelAdmin
            # used to register the model.
            # We're going to check for ForeignKeys to 'pages.Page' since they'll
            # have to have one to be registered as a content inline.

            url = self.check_inline_for_admin_url(obj, inline, Page)

            if url:
                return url

        # If none of the above work then we're really out of options. Just
        # return None and let our caller handle this.
        return None

    def used_on(self, obj=None):
        context = {}
        if obj:
            related_objs = []

            for related in get_candidate_relations_to_delete(obj._meta):
                related_objs = related_objs + list(related.related_model._base_manager.using(DEFAULT_DB_ALIAS).filter(
                    **{"%s__in" % related.field.name: [obj]}
                ))
            context['related_objects'] = [
                {
                    'title': str(obj),
                    'model_name': obj._meta.verbose_name,
                    'admin_url': self.get_admin_url(obj),
                } for obj in related_objs
            ]

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
