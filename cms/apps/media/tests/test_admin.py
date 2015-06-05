from __future__ import unicode_literals

from django.contrib.admin.sites import AdminSite
from django.contrib.admin.views.main import IS_POPUP_VAR
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import Http404
from django.test import TestCase, LiveServerTestCase, RequestFactory
from django.utils import six
from django.utils.timezone import now

from ..admin import FileAdminBase, VideoAdmin
from ..models import File, Label, Video

import base64
import json
import random


class BrokenFile(object):

    """
    A special class designed to raise an IOError the second time it's `file`
    method is called. Used to test sorl.
    """

    name_requested = False

    def __getattr__(self, name):
        if name == 'file':
            if not self.name_requested:
                self.name_requested = True
                return self.obj.file
            return self.obj.file.file
        return getattr(self.obj, name)

    def __init__(self, *args, **kwargs):
        self.obj = File.objects.create(**kwargs)


class MockSuperUser(object):
    pk = 1
    is_active = True
    is_staff = True

    def has_perm(self, perm):
        return True


class TestVideoAdmin(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.video_admin = VideoAdmin(Video, self.site)

        factory = RequestFactory()
        self.request = factory.get('/')

    def test_videoadmin_to_field_allowed(self):
        self.assertTrue(self.video_admin.to_field_allowed(self.request, 'id'))
        self.assertFalse(self.video_admin.to_field_allowed(self.request, 'foo'))


class TestFileAdminBase(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.file_admin = FileAdminBase(File, self.site)

        self.factory = RequestFactory()
        self.request = self.factory.get('/')

        # An invalid JPEG
        self.name_1 = '{}-{}.jpg'.format(
            now().strftime('%Y-%m-%d_%H-%M-%S'),
            random.randint(0, six.MAXSIZE)
        )

        self.obj_1 = File.objects.create(
            title="Foo",
            file=SimpleUploadedFile(self.name_1, b"data", content_type="image/jpeg")
        )

        # A valid GIF.
        self.name_2 = '{}-{}.gif'.format(
            now().strftime('%Y-%m-%d_%H-%M-%S'),
            random.randint(0, six.MAXSIZE)
        )

        base64_string = b'R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='
        self.obj_2 = File.objects.create(
            title="Foo",
            file=SimpleUploadedFile(self.name_2, base64.b64decode(base64_string), content_type="image/gif")
        )

        self.label = Label.objects.create(
            name="Foo"
        )

    def tearDown(self):
        self.obj_1.file.delete(False)
        self.obj_1.delete()

    def test_fileadminbase_to_field_allowed(self):
        self.assertTrue(self.file_admin.to_field_allowed(self.request, 'id'))
        self.assertFalse(self.file_admin.to_field_allowed(self.request, 'foo'))

    def test_fileadminbase_add_label_action(self):
        self.assertEqual(self.obj_1.labels.count(), 0)

        self.file_admin.add_label_action(self.request, File.objects.all(), self.label)

        self.assertEqual(self.obj_1.labels.count(), 1)

    def test_fileadminbase_remove_label_action(self):
        self.assertEqual(self.obj_1.labels.count(), 0)

        self.obj_1.labels.add(self.label)

        self.assertEqual(self.obj_1.labels.count(), 1)

        self.file_admin.remove_label_action(self.request, File.objects.all(), self.label)

        self.assertEqual(self.obj_1.labels.count(), 0)

    def test_fileadminbase_get_actions(self):
        actions = self.file_admin.get_actions(self.request)
        self.assertEqual(len(actions), 2)

        self.request = self.factory.get('/?{}'.format(IS_POPUP_VAR))
        actions = self.file_admin.get_actions(self.request)
        self.assertEqual(len(actions), 0)

    def test_fileadminbase_get_size(self):
        # Why this has to use a unicode space, I don't know..
        self.assertEqual(self.file_admin.get_size(self.obj_1), six.text_type('4\xa0bytes'))

        obj = File.objects.create(
            title="Foo",
            file='media/not/a/real.file'
        )

        self.assertEqual(self.file_admin.get_size(obj), '0 bytes')

    def test_fileadminbase_get_preview(self):
        self.assertEqual(
            self.file_admin.get_preview(self.obj_1),
            '<img cms:permalink="/r/{}-{}/" src="media/img/image-x-generic.png" width="66" height="66" alt="" title="Foo"/>'.format(
                ContentType.objects.get_for_model(File).pk,
                self.obj_1.pk
            )
        )

        # We can't do an `assertEqual` here as the generated src URL is dynamic.
        preview = self.file_admin.get_preview(self.obj_2)

        self.assertIn(
            '<img cms:permalink="/r/{}-{}/"'.format(
                ContentType.objects.get_for_model(File).pk,
                self.obj_2.pk
            ),
            preview,
        )

        self.assertIn(
            'width="66" height="66" alt="" title="Foo"/>',
            preview,
        )

        obj = BrokenFile(
            title="Foo",
            file='media/not/a/real.png'
        )

        # print obj.file
        preview = self.file_admin.get_preview(obj)

        self.assertEqual(preview, '<img cms:permalink="/r/{}-{}/" src="media/img/image-x-generic.png" width="66" height="66" alt="" title="Foo"/>'.format(
            ContentType.objects.get_for_model(File).pk,
            obj.pk
        ))

        obj = File.objects.create(
            title="Foo",
            file='media/not/a/real.file'
        )
        preview = self.file_admin.get_preview(obj)

        self.assertEqual(preview, '<img cms:permalink="/r/{}-{}/" src="/static/media/img/text-x-generic-template.png" width="66" height="66" alt="" title="Foo"/>'.format(
            ContentType.objects.get_for_model(File).pk,
            obj.pk
        ))

    def test_fileadminbase_get_title(self):
        self.assertEqual(self.file_admin.get_title(self.obj_1), 'Foo')

    def test_fileadminbase_response_add(self):
        # Allow the messages framework to work.
        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)
        self.request.user = MockSuperUser()

        response = self.file_admin.response_add(self.request, self.obj_1)
        self.assertEqual(response.status_code, 302)

        self.request = self.factory.get('/?_redactor')
        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)
        self.request.user = MockSuperUser()
        self.request.pages = {}

        response = self.file_admin.response_add(self.request, self.obj_1)
        self.assertEqual(response.status_code, 200)

    def test_fileadminbase_changelist_view(self):
        self.request.user = MockSuperUser()
        view = self.file_admin.changelist_view(self.request)

        self.assertEqual(view.status_code, 200)
        self.assertEqual(view.template_name, 'admin/media/file/change_list.html')
        self.assertNotIn('foo', view.context_data)

        view = self.file_admin.changelist_view(self.request, extra_context={'foo': 'bar'})

        self.assertEqual(view.status_code, 200)
        self.assertEqual(view.template_name, 'admin/media/file/change_list.html')
        self.assertIn('foo', view.context_data)

    def test_fileadminbase_redactor_data(self):
        self.request.user = MockSuperUser()
        data = self.file_admin.redactor_data(self.request)

        self.assertEqual(
            json.loads(data.content.decode()),
            json.loads('{{"objects": [{{"url": "/r/{content_type}-{pk1}/", "title": "Foo"}}, {{"url": "/r/{content_type}-{pk2}/", "title": "Foo"}}], "page": 1, "pages": [1]}}'.format(
                pk1=self.obj_1.pk,
                pk2=self.obj_2.pk,
                content_type=ContentType.objects.get_for_model(File).pk,
            ))
        )

        self.request.user.has_perm = lambda x: False
        data = self.file_admin.redactor_data(self.request)
        self.assertEqual(data.status_code, 403)
        self.request.user.has_perm = lambda x: True

        data = self.file_admin.redactor_data(self.request, file_type='images')
        self.assertEqual(len(data.content), 258)

    def test_fileadminbase_redactor_upload(self):
        self.request.user = MockSuperUser()
        response = self.file_admin.redactor_upload(self.request, '')

        # 405: Method not allowed. We have to POST to this view.
        self.assertEqual(response.status_code, 405)

        self.request.user.has_perm = lambda x: False

        data = self.file_admin.redactor_upload(self.request, '')

        self.assertEqual(data.status_code, 403)

        self.request.user.has_perm = lambda x: True

        self.request.method = 'POST'
        response = self.file_admin.redactor_upload(self.request, '')
        self.assertEqual(response.content, b'')

        response = self.file_admin.redactor_upload(self.request, 'image')
        self.assertEqual(response.content, b'')

        self.request = self.factory.post('/', data={
            'file': self.obj_1.file
        })
        self.request.user = MockSuperUser()

        response = self.file_admin.redactor_upload(self.request, 'image')

        self.assertEqual(json.loads(response.content.decode()), json.loads('{{"filelink": "/r/{}-{}/"}}'.format(
            ContentType.objects.get_for_model(File).pk,
            File.objects.all().order_by('-pk')[0].pk
        )))

        self.request = self.factory.post('/', data={
            'file': SimpleUploadedFile('xoxo.pdf', b"data")
        })
        self.request.user = MockSuperUser()

        response = self.file_admin.redactor_upload(self.request, 'image')
        self.assertEqual(response.content, b'')

        response = self.file_admin.redactor_upload(self.request, 'pdf')

        self.assertEqual(json.loads(response.content.decode()), json.loads('{{"filelink": "/r/{}-{}/", "filename": "xoxo.pdf"}}'.format(
            ContentType.objects.get_for_model(File).pk,
            File.objects.all().order_by('-pk')[0].pk
        )))


class LiveServerTestFileAdminBase(LiveServerTestCase):

    def setUp(self):
        self.site = AdminSite()
        self.file_admin = FileAdminBase(File, self.site)

        self.factory = RequestFactory()
        self.request = self.factory.get('/')

        # An invalid JPEG
        self.name_1 = '{}-{}.jpg'.format(
            now().strftime('%Y-%m-%d_%H-%M-%S'),
            random.randint(0, six.MAXSIZE)
        )

        self.obj_1 = File.objects.create(
            title="Foo",
            file=SimpleUploadedFile(self.name_1, b"data", content_type="image/jpeg")
        )

    def tearDown(self):
        self.obj_1.file.delete(False)
        self.obj_1.delete()

    def test_fileadminbase_remote_view(self):
        self.request.user = MockSuperUser()
        view = self.file_admin.remote_view(self.request, self.obj_1.pk)

        # 405: Method not allowed. We have to POST to this view.
        self.assertEqual(view.status_code, 405)

        self.request.method = 'POST'

        # No URL supplied.
        with self.assertRaises(Http404):
            view = self.file_admin.remote_view(self.request, self.obj_1.pk)

        # No permissions.
        self.request.user.has_perm = lambda x: False

        view = self.file_admin.remote_view(self.request, self.obj_1.pk)
        self.assertEqual(view.status_code, 403)

        self.request.user.has_perm = lambda x: True

        # Allow the messages framework to work.
        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)
        self.request.user = MockSuperUser()

        self.request.POST = {
            'url': self.live_server_url + '/static/media/img/text-x-generic.png'
        }
        view = self.file_admin.remote_view(self.request, self.obj_1.pk)

        self.assertEqual(view.content, b'{"status": "ok"}')
        self.assertEqual(view.status_code, 200)

    # def test_fileadminbase_
