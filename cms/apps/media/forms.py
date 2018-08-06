import base64
import os

from django.core.files.base import ContentFile
from django import forms
from io import BytesIO
from PIL import Image

from cms.apps.media.models import File


class ImageChangeForm(forms.ModelForm):
    changed_image = forms.CharField(
        widget=forms.HiddenInput,
        required=False,
    )

    class Meta:
        model = File
        fields = ['changed_image', 'title', 'file', 'attribution', 'copyright', 'alt_text', 'labels']

    def save(self, commit=True):
        if self.cleaned_data['changed_image']:
            # get image data from canvas output and convert it into an image.
            original = self.instance
            image_data = self.cleaned_data['changed_image']
            format, imgstr = image_data.split(';base64,')
            original_file_name = os.path.basename(original.file.name)
            # rsplit on underscores to prevent the file as being saved with increasingly long names i.e
            # file_AS8Cs2_yb93Df_r87fdc.png if it's been edited 3 times.
            original_file_name = os.path.splitext(original_file_name)[0].rsplit('_', 1)[0]
            file_name = original_file_name + '.' + format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=file_name)

            if original.file.name.split('.')[-1].lower in ('jpeg', 'jpg'):
                # Remove alpha channel and compress to jpg.
                image = Image.open(data)
                image.load()  # required for png.split()
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])  # 3 is the alpha channel
                new_file_name = original_file_name + '.jpg'
                thumb_io = BytesIO()
                background.save(thumb_io, 'JPEG', quality=100)

                self.cleaned_data['file'].save(new_file_name, content=ContentFile(thumb_io.getvalue()), save=False)

            else:
                self.cleaned_data['file'].save(file_name, data)

        return super(ImageChangeForm, self).save(commit=commit)
