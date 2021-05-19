from django.contrib import admin

from cms.apps.pages.admin import page_admin
from cms.apps.testing_models.models import TestInlineModelNoPage, TestInlineModel, TestPageContentWithFields


# Test-only model admins
class TestInlineModelNoPageInline(admin.StackedInline):
    model = TestInlineModelNoPage


class TestInlineModelInline(admin.StackedInline):
    model = TestInlineModel

page_admin.register_content_inline(TestPageContentWithFields, TestInlineModelInline)
