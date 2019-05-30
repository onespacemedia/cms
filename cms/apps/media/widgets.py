from django import forms
from django.utils.html import mark_safe
from django.contrib.admin.widgets import ForeignKeyRawIdWidget

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
                output.append(u' <a href="%s" target="_blank"><img src="%s" alt="%s" width="150" height="150"/></a> %s ' % \
                            (image_url, image_url, file_name, 'Change:'))
        output.append(super().render(name, value, attrs))
        return mark_safe(u''.join(output))

