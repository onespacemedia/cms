from django.forms import widgets


class SmallTexarea(widgets.Textarea):
    def __init__(self, attrs={}):
        attrs.update({
            'style': 'width: calc(100% - 15px); resize: none;',
            'rows': '4'
        })

        super(SmallTexarea, self).__init__(attrs)
