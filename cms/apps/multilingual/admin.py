from copy import deepcopy
from functools import update_wrapper
from random import randint

from cms.admin import get_last_modified
from cms.apps.multilingual.models import MultilingualObject
from cms.apps.multilingual.widgets import SmallTexarea
from cms.apps.pages.models import Page, ContentBase
from django import forms
from django.contrib import admin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse

MULTILINGUAL_ADMIN_FIELDS = ['admin_name']
MULTILINGUAL_LANGUAGE_FIELDS = ['parent', 'language', 'version', 'published']


class MultilingualObjectAdminForm(forms.ModelForm):
    class Meta:
        widgets = {
            'admin_description': SmallTexarea,
            'admin_notes': SmallTexarea,
        }


class MultilingualObjectAdmin(admin.ModelAdmin):
    list_display = ['admin_name', 'get_date_modified']
    form = MultilingualObjectAdminForm
    change_list_template = "admin/multilingual/multilingualobject/change_list.html"
    change_form_template = "admin/multilingual/multilingualobject/change_form.html"

    def get_fields(self, request, obj=None):
        # Get base fields
        fields = super(MultilingualObjectAdmin, self).get_fields(request, obj)

        # Create new fields array
        new_fields = []

        # Loop the base fields and only add those we want
        for field in fields:
            if field not in MULTILINGUAL_ADMIN_FIELDS:
                new_fields.append(field)

        # Return new fields
        return new_fields

    def get_fieldsets(self, request, obj=None):
        # If we have pre-defined fieldsets, add the admin fields to those for the user
        if self.fieldsets:
            return [
                       ("Admin options", {'fields': MULTILINGUAL_ADMIN_FIELDS})
                   ] + self.fieldsets

        # We have no fieldsets, so ust generate a basic admin content field split
        fieldsets = [
            ("Admin options", {'fields': MULTILINGUAL_ADMIN_FIELDS}),
        ]
        fields = self.get_fields(request, obj)
        if fields:
            fieldsets.append(
                ("Content", {'fields': fields})
            )
        return fieldsets

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):

        # Get the multilingual object
        if object_id:
            multilingual_object = get_object_or_404(self.model, pk=object_id)

            # Get the multilingual object translation objects
            extra_context = dict(
                translation_objects=multilingual_object.translation_objects(),
            )
        else:
            extra_context = dict(
                hide_translations=True,
            )

        return super(MultilingualObjectAdmin, self).changeform_view(request, object_id, form_url, extra_context)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(MultilingualObjectAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

        # if db_field.name == 'page':
        #     if issubclass(self.model, MultilingualObject):
        #         field.queryset = Page.objects.filter(pk__in=self.model.objects.values_list('page_id', flat=True))

        return field

    def get_date_modified(self, obj):
        obj_content = obj.content()
        return get_last_modified(obj_content)
    get_date_modified.short_description = 'Last modified'


class MultilingualTranslationAdmin(admin.ModelAdmin):

    list_display = ['__str__', 'language', 'version', 'published', 'get_date_modified']

    change_form_template = "admin/multilingual/multilingualtranslation/change_form.html"

    def get_urls(self):
        from django.conf.urls import url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        urlpatterns = [
            url(r'^$', wrap(self.changelist_view), name='%s_%s_changelist' % info),
            url(r'^add/$', wrap(self.add_view), name='%s_%s_add' % info),
            url(r'^duplicate/$', wrap(self.duplicate_view), name='%s_%s_duplicate' % info),
            url(r'^(.+)/history/$', wrap(self.history_view), name='%s_%s_history' % info),
            url(r'^(.+)/delete/$', wrap(self.delete_view), name='%s_%s_delete' % info),
            url(r'^(.+)/$', wrap(self.change_view), name='%s_%s_change' % info),
        ]
        return urlpatterns

    def get_form(self, request, obj=None, **kwargs):
        # Get base form
        form = super(MultilingualTranslationAdmin, self).get_form(request, obj, **kwargs)

        # If we have a parent ID in get, set it to form
        if request.GET.get('parent', None):
            form.base_fields['parent'].initial = request.GET.get('parent', None)

        form.base_fields['parent'].verbose_name = 'Object'
        form.base_fields['parent'].help_text = 'Object which this translation is bound to'

        # Return modified form
        return form

    def get_fields(self, request, obj=None):
        # Get base fields
        fields = super(MultilingualTranslationAdmin, self).get_fields(request, obj)

        # Create new fields array
        new_fields = []

        # Loop the base fields and only add those we want
        for field in fields:
            if field not in MULTILINGUAL_LANGUAGE_FIELDS:
                new_fields.append(field)

        # Return new fields
        return new_fields

    def get_fieldsets(self, request, obj=None):
        # If we have pre-defined fieldsets, add the admin fields to those for the user
        if self.fieldsets:
            return [
                       ("Language", {'fields': MULTILINGUAL_LANGUAGE_FIELDS})
                   ] + self.fieldsets

        # We have no fieldsets, so ust generate a basic admin content field split
        fieldsets = [
            ("Language", {'fields': MULTILINGUAL_LANGUAGE_FIELDS}),
        ]
        fields = self.get_fields(request, obj)
        if fields:
            fieldsets.append(
                ("Content", {'fields': fields})
            )

        return fieldsets

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(MultilingualTranslationAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

        if db_field.name == 'parent':
            field.label_from_instance = lambda obj: obj.admin_name

        return field

    def duplicate_view(self, request, *args, **kwargs):
        # Get the content object we are going to duplicate
        content_object = get_object_or_404(self.model, pk=request.GET.get('content_object', None))

        # If the user has come from the post request and its a yes...
        if request.method == 'POST' and request.POST.get('post', 'no') == 'yes':

            # Duplicate the content object
            new_content_object = deepcopy(content_object)
            new_content_object.pk = None  # Strip pk to save as a valid copy
            new_content_object.published = False
            new_content_object.version = content_object.version + 1
            new_content_object.save()

            for link in dir(content_object):
                if link.endswith('_set') and getattr(content_object,
                                                     link).__class__.__name__ == "RelatedManager" and link not in [
                    'child_set', 'owner_set', 'link_to_page']:
                    objects = getattr(content_object, link).all()
                    for content_related_object in objects:

                        # Get related field names
                        related_fields = [field.name for field in content_related_object._meta.fields if field.related_model == self.model]

                        if related_fields:
                            new_content_related_object = deepcopy(content_related_object)
                            new_content_related_object.pk = None
                            setattr(new_content_related_object, related_fields[0], new_content_object)
                            new_content_related_object.save()

            messages.add_message(request, messages.INFO, 'The content object has been duplicated successfully!')
            return redirect('admin:{}_{}_change'.format(
                self.model._meta.app_label,
                self.model._meta.model_name
            ), *[new_content_object.pk])

        # Template context
        context = dict(
            content_object=content_object
        )

        # Render template
        return TemplateResponse(request, 'admin/multilingual/multilingualobject/language_duplicate.html', context)

    def get_date_modified(self, obj):
        return get_last_modified(obj)
    get_date_modified.short_description = 'Last modified'
