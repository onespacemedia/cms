from django import forms
from django.utils.html import mark_safe
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.utils.html import format_html


class ImageThumbnailWidget(ForeignKeyRawIdWidget):
    '''
    A widget used to display a thumbnail image preview
    '''
    template_name = 'admin/widgets/image_raw_id.html'

    def get_context(self, name, value, attrs):
        # Import here to avoid circular dependencies
        from .models import File

        context = super().get_context(name, value, attrs)
        if value:
            context['file_obj'] = File.objects.get(pk=value)
        return context
