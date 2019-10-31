# Moderation system

Sometimes it is useful for certain admin users to be able to create and edit objects, such as news articles, but to not be able to publish them immediately.
The CMS has a simple, entirely optional system for facilitating this.
Models which utilise this moderation system gain a field named `status` which has three possible values: "Draft", "Submitted for approval" or "Approved".
Objects are only visible on the front-end of the website when they are marked as "Approved".

Adding the moderation system to a model will create a new permission named "Can approve items".
Users will need to have this permission to be able to publish items to the website by changing the object's status to "Approved".
Users without the permission will only be able to set the object's status to "Draft" or "Submitted for approval".

## Adding the moderation system to a model

First, modify your model:

```python
from cms.plugins.moderation.models import ModerationBase

class MyModel(ModerationBase):
    # Your fields here.

    # If you have Meta options, they should extend ModerationBase.Meta.
    class Meta(ModerationBase.Meta):
        pass
```

To integrate the moderation system with the Django admin, modify your ModelAdmin to take this form:

```python
from cms.plugins.moderation.admin import MODERATION_FIELDS, ModerationAdminBase
from django.contrib import admin

from .models import MyModel


@admin.register(MyModel)
class MyModelAdmin(ModerationAdminBase):
    fieldsets = [
        # ...your fieldsets here...
        MODERATION_FIELDS,
    ]
```

If your model already existed before adding the moderation system you will need to run `./manage.py update_permissions` (and probably restart the server) before they appear.
