from django.test import TestCase
from django.utils import six

from ..debug import print_exc, print_current_exc

import os

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import sys
import unittest


class TestDebug(TestCase):

    @unittest.skipIf(six.PY3, "Not applicable to Python 3.")
    def test_print_exc(self):
        def func():
            return True

        def func_raise():
            raise Exception

        self.assertEqual(print_exc(func), func)

        self.orig_stderr = sys.stderr
        sys.stderr = open(os.devnull, 'w')

        with self.settings(DEBUG=True):
            self.assertTrue(print_exc(func)())

            with self.assertRaises(Exception):
                print_exc(func_raise)()

        sys.stderr = self.orig_stderr

    @unittest.skipIf(six.PY3, "Not applicable to Python 3.")
    def test_print_current_exc(self):
        # Redirect STDOUT so we can capture the `print`.
        orig_stderr = sys.stderr
        stderr = StringIO()
        sys.stderr = stderr

        print_current_exc()

        with self.settings(DEBUG=True):
            print_current_exc()

        self.assertEqual(stderr.getvalue().strip(), 'None')

        sys.stderr = orig_stderr
