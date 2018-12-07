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
            # Get image data from canvas and decode it; this will always be
            # in base64-encoded PNG format:
            # data:image/png;base64,[...image data....]
            changed_image = self.cleaned_data['changed_image']
            image_data = base64.b64decode(changed_image.split(';base64,')[1])
            root_name, extension = os.path.splitext(
                os.path.basename(self.instance.file.name)
            )

            # Each time a file is saved, Django will append _XXXXX until the
            # file name is unique. Taking the part before the first underscore
            # will prevent files being given increasingly long names, e.g.
            # file_AS8Cs2_yb93Df_r87fdc.jpg if it's been edited 3 times.
            #
            # The tradeoff is that if an image is uploaded as
            # Flowering_Cherry_Tree.jpg, the first time it is edited it will
            # be saved as Flowering_Cherry.jpg. This is less bad than the
            # alternative.
            new_file_name = '{}{}'.format(root_name.rsplit('_', 1)[0], extension)
            content_file = ContentFile(image_data, name=new_file_name)

            if extension.lower() in ('.jpeg', '.jpg'):
                # Remove alpha channel for JPEGs - attempting to save with an
                # alpha channel still present will throw an exception.
                image = Image.open(content_file)
                image.load()  # required for png.split()
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])  # 3 is the alpha channel
                thumb_io = BytesIO()
                # Each save of a JPEG results in a small amount of degradation;
                # use quality=100 to limit this.
                background.save(thumb_io, 'JPEG', quality=100)

                self.cleaned_data['file'].save(
                    new_file_name, content=ContentFile(thumb_io.getvalue()), save=False
                )

            else:
                self.cleaned_data['file'].save(new_file_name, content=content_file)

        return super().save(commit=commit)
