from django.contrib import admin

from .models import APPROVED, STATUS_CHOICES

MODERATION_FIELDS = ('Moderation controls', {
    'fields': ['status']
})


class ModerationAdminBase(admin.ModelAdmin):

    fieldsets = (MODERATION_FIELDS,)

    list_filter = ['status']

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        '''
        Give people who have the permission to approve item an extra option to
        change the status to approved.
        '''

        if db_field.name == 'status':
            choices_list = STATUS_CHOICES

            # Check if the user has permission to approve this model's objects.
            if not request.user.has_perm('{}.can_approve'.format(db_field.model._meta.app_label)):
                choices_list = [x for x in STATUS_CHOICES if x[0] != APPROVED]

            kwargs['choices'] = choices_list

        return super().formfield_for_choice_field(db_field, request, **kwargs)
