Moderation Plugin
=================

Built into the CMS is a fully featured moderation system which allows any model in your project to be controlled by a status system.  Models which utilise the moderation system gain a field named ``status`` which has three possible values: "Draft", "Submitted for approval" or "Approved". Objects are only visible on the front-end of the website when they are marked as "Approved".

Adding the moderation system to a model will create a new permission to be created named "Can approve items". Users will need to have this permission to be able to publish items to the website by setting the object status to "Approved", users without the permission will only be able to set the object status to "Draft" or "Submitted for approval".

Adding the moderation system to a model
---------------------------------------

There are a few steps required to integrate the moderation system with your models.  You will need to modify your models.py to look like this::

    from cms.plugins.moderation.models import ModerationBase

    class MyModel(ModerationBase):

        # If you wish to set Meta settings, you need to extend ModerationBase.Meta.
        class Meta(ModerationBase.Meta):
            pass


To integrate the moderation system with the Django admin system modify your admin.py to use this structure::


    from django.contrib import admin

    from .models import MyModel

    from cms.plugins.moderation.admin import MODERATION_FIELDS, ModerationAdminBase


    class MyModelAdmin(ModerationAdminBase):

        # If your fieldsets variable only contains MODERATION_FIELDS, you can omit
        # this variable entirely as this configuration is the default.
        fieldsets = (
            MODERATION_FIELDS,
        )

    admin.site.register(MyModel, MyModelAdmin)

If your model already existed before adding the moderation system you will need to run ``./manage.py update_permissions`` (and probably restart the server) before they appear.
