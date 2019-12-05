from django.contrib import admin

from cms.apps.testing_models.models import TestInlineModelNoPage, TestInlineModel


# Test-only model admins
class TestInlineModelNoPageInline(admin.StackedInline):
    model = TestInlineModelNoPage


class TestInlineModelInline(admin.StackedInline):
    model = TestInlineModel
