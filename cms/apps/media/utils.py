from django.conf import settings

def timedelta_to_iso8601(value):
    if not value:
        return ''

    # split seconds to larger units
    seconds = value.total_seconds()
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    days, hours, minutes = map(int, (days, hours, minutes))
    seconds = round(seconds, 6)

    ## build date
    date = ''
    if days:
        date = '%sD' % days

    ## build time
    time = u'T'

    # hours
    bigger_exists = date or hours
    if bigger_exists:
        time += '{:02}H'.format(hours)

    # minutes
    bigger_exists = bigger_exists or minutes
    if bigger_exists:
      time += '{:02}M'.format(minutes)

    # seconds
    if seconds.is_integer():
        seconds = '{:02}'.format(int(seconds))
    else:
        # 9 chars long w/leading 0, 6 digits after decimal
        seconds = '%09.6f' % seconds

    # remove trailing zeros
    seconds = seconds.rstrip('0')
    time += '{}S'.format(seconds)

    return u'P' + date + time

def url_from_path(path, request=None):
    if path.startswith('http://') or path.startswith('https://'):
        return path

    if not path.startswith('/'):
        path = '/' + path

    if request and not request.is_secure():
        secure_part = ''
    else:
        secure_part = 's'

    return f'http{secure_part}://{settings.SITE_DOMAIN}{path}'
