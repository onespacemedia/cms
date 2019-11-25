from django.contrib import admin

from cms.apps.testing_models.models import InlineModelNoPage, InlineModel


# Test-only model admins
class InlineModelNoPageInline(admin.StackedInline):
    model = InlineModelNoPage


class InlineModelInline(admin.StackedInline):
    model = InlineModel
