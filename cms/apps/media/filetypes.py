import os.path

from django.contrib.staticfiles.storage import staticfiles_storage


# Different types of file.
AUDIO_FILE_ICON = staticfiles_storage.url('media/img/audio-x-generic.png')
DOCUMENT_FILE_ICON = staticfiles_storage.url('media/img/x-office-document.png')
SPREADSHEET_FILE_ICON = staticfiles_storage.url('media/img/x-office-spreadsheet.png')
TEXT_FILE_ICON = staticfiles_storage.url('media/img/text-x-generic.png')
IMAGE_FILE_ICON = staticfiles_storage.url('media/img/image-x-generic.png')
MOVIE_FILE_ICON = staticfiles_storage.url('media/img/video-x-generic.png')
UNKNOWN_FILE_ICON = staticfiles_storage.url('media/img/text-x-generic-template.png')

# Recognised file extensions and their icons.
FILE_ICONS = {
    'mp3': AUDIO_FILE_ICON,
    'm4a': AUDIO_FILE_ICON,
    'wav': AUDIO_FILE_ICON,
    'doc': DOCUMENT_FILE_ICON,
    'docx': DOCUMENT_FILE_ICON,
    'odt': DOCUMENT_FILE_ICON,
    'pdf': DOCUMENT_FILE_ICON,
    'xls': SPREADSHEET_FILE_ICON,
    'xlsx': SPREADSHEET_FILE_ICON,
    'txt': TEXT_FILE_ICON,
    'flv': MOVIE_FILE_ICON,
    'm4v': MOVIE_FILE_ICON,
    'mp4': MOVIE_FILE_ICON,
    'mov': MOVIE_FILE_ICON,
    'swf': MOVIE_FILE_ICON,
    'webm': MOVIE_FILE_ICON,
    'wmv': MOVIE_FILE_ICON,
}

IMAGE_FILE_EXTENSIONS = ['gif', 'png', 'jpg', 'jpeg']

for ext in IMAGE_FILE_EXTENSIONS:
    FILE_ICONS[ext] = IMAGE_FILE_ICON


def is_image(filename):
    '''
    Returns True if an image's extension suggests it is a file, False
    otherwise. It does no validation of the contents of the file.
    '''
    _, extension = os.path.splitext(filename)
    extension = extension.lower()[1:]
    return extension in IMAGE_FILE_EXTENSIONS


def get_icon_for_extension(extension):
    '''Returns an appropriate icon for the given file extension.'''
    return FILE_ICONS.get(extension, UNKNOWN_FILE_ICON)


def get_icon(filename):
    '''Returns an appropriate icon for the given filename.'''
    _, extension = os.path.splitext(filename)
    extension = extension[1:]
    return get_icon_for_extension(extension)
