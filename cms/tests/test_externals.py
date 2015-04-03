from django.test import TestCase

from ..externals import External

try:
    from contextlib import GeneratorContextManager
except ImportError:
    from contextlib import _GeneratorContextManager as GeneratorContextManager

from types import FunctionType


class TestExternals(TestCase):

    def test_load(self):
        external = External('foo')

        with self.assertRaises(ImportError):
            external._load('')

    def test_load_class(self):
        external = External('foo')

        self.assertIsInstance(external.load_class(''), object)
        self.assertTrue(external.load_class('', fallback=True))

    def test_load_method(self):
        external = External('foo')
        self.assertIsNone(external.load_method('')())
        self.assertTrue(external.load_method('', fallback=True))

    def test_context_manager(self):
        external = External('foo')
        self.assertIs(type(external.context_manager('')), FunctionType)
        self.assertIsInstance(external.context_manager('')(), GeneratorContextManager)
        self.assertTrue(external.context_manager('', fallback=True))

        with external.context_manager('')():
            self.assertTrue(True)
