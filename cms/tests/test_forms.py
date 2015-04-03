from django.test import TestCase

from ..forms import CMSPasswordChangeForm, CMSAdminPasswordChangeForm, HtmlWidget, password_validation


class MockSuperUser(object):

    pk = 1

    def check_password(self, password):
        return True

    def has_perm(self, perm):
        return True


class TestForms(TestCase):

    def test_htmlwidget_init(self):
        widget = HtmlWidget()
        self.assertIsInstance(widget, HtmlWidget)

    def test_htmlwidget_get_media(self):
        widget = HtmlWidget()

        media = widget.get_media()

        self.assertDictEqual(media.__dict__, {
            '_css': {
                'all': ['cms/js/redactor/redactor.css']
            },
            '_js': [
                '/static/cms/js/jquery.cms.js',
                '/static/cms/js/jquery.cookie.js',
                '/static/pages/js/jquery.cms.pages.js',
                '/static/cms/js/redactor/redactor.js',
                '/static/cms/js/redactor/plugins/table/table.js',
                '/static/cms/js/redactor/plugins/imagemanager/imagemanager.js',
                '/static/cms/js/redactor/plugins/video/video.js',
                '/static/cms/js/redactor/plugins/filemanager/filemanager.js'
            ]
        })

    def test_htmlwidget_render(self):
        # Sorry for the long strings in this one..
        widget = HtmlWidget()
        rendered = widget.render('foo', 'bar')

        self.assertEqual(
            rendered,
            '<textarea class="redactor" cols="40" name="foo" rows="10">\r\nbar<' +
            '/textarea>'
        )

        rendered = widget.render('foo', 'bar', attrs={'id': 'foo'})

        self.assertIn(
            '<textarea class="redactor" cols="40" id="foo" name="foo" rows="10">',
            rendered,
        )

        self.assertIn(
            '"fileUpload": "/admin/media/file/redactor/upload/file/"',
            rendered,
        )

        self.assertIn(
            '"imageUpload": "/admin/media/file/redactor/upload/image/"',
            rendered,
        )

        self.assertIn(
            '"minHeight": 300',
            rendered,
        )

    def test_password_validation(self):
        self.assertListEqual(password_validation(''), [
            'Your password needs to be at least 8 characters long.',
            'Your password needs include at least 1 uppercase character.',
            'Your password needs include at least 1 lowercase character.',
            'Your password needs include at least 1 number.',
            'Your password needs include at least 1 special character.'
        ])

        self.assertListEqual(password_validation('P@ssw0rd!'), [])

    def test_cmspasswordchangeform_clean_new_password1(self):
        user = MockSuperUser()
        form = CMSPasswordChangeForm(user, data={
            'old_password': '123456',
            'new_password1': '123456',
            'new_password2': '123456'
        })

        self.assertFalse(form.is_valid())
        self.assertDictEqual(form._errors, {
            'new_password1': [
                'Your password needs to be at least 8 characters long.',
                'Your password needs include at least 1 uppercase character.',
                'Your password needs include at least 1 lowercase character.',
                'Your password needs include at least 1 special character.'
            ]
        })

        form = CMSPasswordChangeForm(user, data={
            'old_password': '123456',
            'new_password1': 'P@ssw0rd',
            'new_password2': 'P@ssw0rd'
        })

        self.assertTrue(form.is_valid())
        self.assertDictEqual(form._errors, {})

    def test_cmsadminpasswordchangeform_clean_new_password1(self):
        user = MockSuperUser()

        self.assertTrue(user.has_perm(''))

        form = CMSAdminPasswordChangeForm(user, data={
            'password1': '123456',
            'password2': '123456'
        })

        self.assertFalse(form.is_valid())
        self.assertDictEqual(form._errors, {
            'password1': [
                'Your password needs to be at least 8 characters long.',
                'Your password needs include at least 1 uppercase character.',
                'Your password needs include at least 1 lowercase character.',
                'Your password needs include at least 1 special character.'
            ]
        })

        form = CMSAdminPasswordChangeForm(user, data={
            'password1': 'P@ssw0rd',
            'password2': 'P@ssw0rd'
        })

        self.assertTrue(form.is_valid())
        self.assertDictEqual(form._errors, {})
