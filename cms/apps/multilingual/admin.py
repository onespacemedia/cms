from functools import update_wrapper

from django import forms
from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin.utils import quote
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils import six


MULTILINGUAL_FIELDS = ('Language', {'fields': ['language', 'version', 'online']})


class MultilingualChangeList(ChangeList):
    def url_for_result(self, result):
        pk = getattr(result, self.pk_attname)
        return reverse('admin:%s_%s_languages' % (self.opts.app_label, self.opts.model_name),
                       kwargs={
                           'obj': quote(pk)
                       },
                       current_app=self.model_admin.admin_site.name)


class MultilingualLanguageList(ChangeList):
    def __init__(self, request, model, list_display, list_display_links, list_filter, date_hierarchy, search_fields,
                 list_select_related, list_per_page, list_max_show_all, list_editable, model_admin):
        super(MultilingualLanguageList, self).__init__(request, model, list_display, list_display_links, list_filter,
                                                       date_hierarchy, search_fields, list_select_related,
                                                       list_per_page, list_max_show_all, list_editable, model_admin)

        self.model = self.model.language_model
        self.list_display = ['language', 'version', 'online']
        self.list_display_links = ['language']

    def url_for_result(self, result):
        return reverse('admin:%s_%s_language' % (self.opts.app_label, self.opts.model_name),
                       kwargs={
                           'obj': result.parent.pk,
                           'lang': result.pk,
                       },
                       current_app=self.model_admin.admin_site.name)


class MultilingualAdmin(admin.ModelAdmin):
    change_list_template = 'admin/multilingual/multilingualmodel/change_list.html'
    change_form_template = 'admin/multilingual/multilingualmodel/change_form.html'
    delete_confirmation_template = 'admin/multilingual/multilingualmodel/delete_confirmation.html'

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        urlpatterns = [
            url(r'^$', wrap(self.changelist_view), name='%s_%s_changelist' % info),
            url(r'^add/$', wrap(self.add_view), name='%s_%s_add' % info),

            url(r'^(?P<obj>\d+)/languages/$', wrap(self.languagelist_view), name='%s_%s_languages' % info),
            url(r'^(?P<obj>\d+)/languages/add/$', wrap(self.languageadd_view),
                name='%s_%s_languageadd' % info),
            url(r'^(?P<obj>\d+)/languages/(?P<lang>\d+)/$', wrap(self.languagechange_view),
                name='%s_%s_language' % info),
            url(r'^(?P<obj>\d+)/languages/(?P<lang>\d+)/delete/$', wrap(self.languagedelete_view),
                name='%s_%s_languagedelete' % info),

            url(r'^(.+)/history/$', wrap(self.history_view), name='%s_%s_history' % info),
            url(r'^(.+)/delete/$', wrap(self.delete_view), name='%s_%s_delete' % info),
            url(r'^(.+)/$', wrap(self.change_view), name='%s_%s_change' % info),
        ]
        return urlpatterns

    def get_multilingual_language_class(self, request, obj):

        # If we have an object, we can skip that and use the language object on the multilingual model
        if obj:

            # If the object doesn't have a language model attr, its probably an actual language model
            if not hasattr(obj, 'language_model'):

                # Try and force the object to the parent
                try:
                    obj = obj.parent
                except:
                    pass

            # Only continue if we have the language model attr
            if hasattr(obj, 'language_model'):
                return ContentType.objects.get_for_model(obj.language_model).model_class()

        else:
            return ContentType.objects.get_for_model(self.model.language_model).model_class()

        # No type was found
        raise Http404("You must specify a language content type.")

    def get_form(self, request, obj=None, **kwargs):

        # Get the class being used for the languages
        language_class = self.get_multilingual_language_class(request, obj)
        form_attrs = {}

        # Loop the fields in the language class
        for field in language_class._meta.fields + language_class._meta.many_to_many:

            # Skip parent, becuase we do this automatically
            if field.name == "parent":
                continue

            # Build form field
            form_field = self.formfield_for_dbfield(field, request=request)

            # Set correct widget on  fields we want as filter horizontals
            if field.name in getattr(language_class, "filter_horizontal", ()):
                form_field.widget = FilteredSelectMultiple(
                    field.verbose_name,
                    is_stacked=False,
                )

            # Store the field.
            form_attrs[field.name] = form_field

        # Create the form with our new fields
        if six.PY2:
            ContentForm = type(six.binary_type("{}Form").format(self.__class__.__name__), (forms.ModelForm,),
                               form_attrs)
        else:
            ContentForm = type(six.text_type("{}Form".format(self.__class__.__name__)), (forms.ModelForm,),
                               form_attrs)

        # Update kwargs with our new form
        defaults = {"form": ContentForm}
        defaults.update(kwargs)

        # Set prepopulated fields for form from model
        self.prepopulated_fields = getattr(language_class, 'prepopulated_fields', {})

        # Return our new form
        return super(MultilingualAdmin, self).get_form(request, obj, **defaults)

    def save_model(self, request, obj, form, change):
        # Get the language model class and content type model
        language_class = self.get_multilingual_language_class(request, obj)

        # If our object is a multilingual object, we are adding a new language
        if isinstance(obj, self.model):
            change = False

        if change:
            obj.save()
        else:
            # Create a new language object
            language_obj = language_class()

            # Loop the fields in our content object and assign fields in our form to the model
            for field in language_obj._meta.fields:
                if form.cleaned_data.get(field.name, None):
                    setattr(language_obj, field.name, form.cleaned_data[field.name])

            # Save the current multilingual object and assign the new initial language object
            obj.save()
            language_obj.parent = obj
            language_obj.save()

    def get_queryset(self, request):
        if request.resolver_match.url_name in [
            '{}_{}_languages'.format(self.opts.app_label, self.opts.model_name),
            '{}_{}_language'.format(self.opts.app_label, self.opts.model_name),
            '{}_{}_languagedelete'.format(self.opts.app_label, self.opts.model_name),
        ]:
            qs = self.model.language_model._default_manager.get_queryset()

            if hasattr(request, 'multilingual_object'):
                qs = qs.filter(parent=request.multilingual_object)
        else:
            qs = self.model._default_manager.get_queryset()

        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)

        print qs

        return qs

    def get_changelist(self, request, **kwargs):
        # If we match the languages list view name, serve the languages list changelist
        if request.resolver_match.url_name in [
            '{}_{}_languages'.format(self.opts.app_label, self.opts.model_name),
        ]:
            return MultilingualLanguageList

        # Return modified onject change list
        return MultilingualChangeList

    def languagelist_view(self, request, extra_context=None, *args, **kwargs):

        multilingual_object = get_object_or_404(self.model, pk=kwargs['obj'])

        # Get the multilingual object if we can
        extra_context = dict(
            multilingual_object=multilingual_object
        )

        # Set object on request for global access
        request.multilingual_object = multilingual_object

        return self.changelist_view(request, extra_context)

    def languageadd_view(self, request, extra_context=None, *args, **kwargs):

        # Get the multilingual object if we can
        extra_context = dict(
            multilingual_object=get_object_or_404(self.model, pk=kwargs['obj'])
        )

        return self.changeform_view(request, kwargs['obj'], '', extra_context)

    def languagechange_view(self, request, extra_context=None, *args, **kwargs):

        # Get the multilingual object if we can
        extra_context = dict(
            multilingual_object=get_object_or_404(self.model, pk=kwargs['obj']),
            is_language=True
        )

        return self.changeform_view(request, kwargs['lang'], '', extra_context)

    def languagedelete_view(self, request, *args, **kwargs):

        # Get the multilingual object if we can
        extra_context = dict(
            multilingual_object=get_object_or_404(self.model, pk=kwargs['obj'])
        )

        return self.delete_view(request, kwargs['lang'], extra_context)

    def response_add(self, request, *args, **kwargs):
        """Redirects to the sitemap if appropriate."""
        response = super(MultilingualAdmin, self).response_add(request, *args, **kwargs)
        return self.patch_response_location(request, response, *args, **kwargs)

    def response_change(self, request, *args, **kwargs):
        """Redirects to the sitemap if appropriate."""
        response = super(MultilingualAdmin, self).response_change(request, *args, **kwargs)
        return self.patch_response_location(request, response, *args, **kwargs)

    def delete_view(self, request, *args, **kwargs):
        """Redirects to the sitemap if appropriate."""
        response = super(MultilingualAdmin, self).delete_view(request, *args, **kwargs)
        return self.patch_response_location(request, response, *args, **kwargs)

    def patch_response_location(self, request, response, *args, **kwargs):
        """Perpetuates the 'from' key in all redirect responses."""
        if request.resolver_match.url_name in [
            '{}_{}_language'.format(self.opts.app_label, self.opts.model_name),
        ]:
            response["Location"] = reverse(
                'admin:%s_%s_languages' % (self.opts.app_label, self.opts.model_name),
                    kwargs={
                        'obj': args[0].parent.pk,
                    })
        elif request.resolver_match.url_name in [
            '{}_{}_languageadd'.format(self.opts.app_label, self.opts.model_name),
        ]:
            response["Location"] = reverse(
                'admin:%s_%s_languages' % (self.opts.app_label, self.opts.model_name),
                kwargs={
                    'obj': args[0].parent.pk,
                })

        return response

    def get_actions(self, request):
        if request.resolver_match.url_name in [
            '{}_{}_languages'.format(self.opts.app_label, self.opts.model_name),
        ]:
            return dict()

        return super(MultilingualAdmin, self).get_actions(request)

    def get_fieldsets(self, request, obj=None):
        # Get super fieldsets
        fieldsets = super(MultilingualAdmin, self).get_fieldsets(request, obj)
        return fieldsets

    def get_ordering(self, request):
        if request.resolver_match.url_name in [
            '{}_{}_languages'.format(self.opts.app_label, self.opts.model_name),
        ]:
            return ('language', 'version')

        return super(MultilingualAdmin, self).get_ordering(request)





