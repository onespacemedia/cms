from cms.apps.multilingual.widgets import SmallTexarea
from cms.apps.pages.models import Page
from django import forms
from django.contrib import admin
from django.shortcuts import get_object_or_404

MULTILINGUAL_ADMIN_FIELDS = ['admin_name']
MULTILINGUAL_LANGUAGE_FIELDS = ['parent', 'language', 'version', 'published']


class MultilingualObjectAdminForm(forms.ModelForm):
    class Meta:
        widgets = {
            'admin_description': SmallTexarea,
            'admin_notes': SmallTexarea,
        }


class MultilingualObjectAdmin(admin.ModelAdmin):
    list_display = ['admin_name']
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

        if db_field.name == 'page':
            field.queryset = Page.objects.filter(pk__in=self.model.objects.values_list('page_id', flat=True))

        return field


class MultilingualTranslationAdmin(admin.ModelAdmin):

    list_display = ['__str__', 'language', 'version', 'published']

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
