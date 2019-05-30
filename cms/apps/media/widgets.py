from django import forms
from django.utils.html import mark_safe
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.utils.html import format_html

class ImageThumbnailWidget(ForeignKeyRawIdWidget):
    '''
    A widget used to display a thumbnail image preview
    '''
    def render(self, name, value, attrs=None):
        # Import here to avoid circular dependencies
        from .models import File
        output = []

        if value:
            file_obj = File.objects.filter(pk=value).first()

            if file_obj:
                image_url = file_obj.file.url
                file_name = str(file_obj)
                output.append(format_html('<a href="{}" target="_blank"><img src="{}" alt="{}" width="150" height="150"/></a> Change:', image_url, image_url, file_name))
        output.append(super().render(name, value, attrs))
        return mark_safe(''.join(output))

