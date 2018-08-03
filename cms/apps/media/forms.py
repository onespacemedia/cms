import base64

from django.conf import settings
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
            original = File.objects.filter(file=self.cleaned_data['file']).first()
            image_data = self.cleaned_data['changed_image']
            format, imgstr = image_data.split(';base64,')
            original_file_name = original.file.name.split('/')[-1].split('.')[0]
            file_name = original_file_name + '.' + format
            data = ContentFile(base64.b64decode(imgstr), name=file_name)

            # Remove alpha channel and compress to jpg.
            image = Image.open(data)
            image.load()  # required for png.split()
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])  # 3 is the alpha channel
            new_file_name = settings.MEDIA_ROOT + '/' + original.file.name.split('.')[0].split('_')[0] + '.jpg'
            thumb_io = BytesIO()
            background.save(thumb_io, 'JPEG', quality=80)

            self.cleaned_data['file'].save(new_file_name.split('/')[-1], content=ContentFile(thumb_io.getvalue()), save=False)

        return super(ImageChangeForm, self).save(commit=commit)
