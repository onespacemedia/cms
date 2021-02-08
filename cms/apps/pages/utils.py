from copy import deepcopy

from django.contrib import admin
from django.db import models
from django.db.models import Q
from django.forms.models import _get_foreign_key
from watson.search import update_index

from .models import Page, publication_manager


def overlay_obj(original, overlay, exclude=None, related_fields=None, commit=False):
    exclude = exclude or []
    deffered_fields = []

    for field in original._meta.get_fields():
        if field.name in exclude:
            continue

        if isinstance(field, models.AutoField):
            continue

        if isinstance(field, (models.ManyToManyField, models.ManyToManyRel, models.ManyToOneRel)):
            if related_fields is None or field.name in related_fields:
                deffered_fields.append(field)
            continue

        setattr(original, field.name, getattr(overlay, field.name))

    if commit:
        original.save()
        for field in deffered_fields:
            if isinstance(field, models.ManyToManyField):
                accessor = field.name
            else:
                accessor = field.get_accessor_name()
            old_qs = getattr(overlay, accessor).all()
            # Delete stale inlines
            if isinstance(field, models.ManyToOneRel):
                getattr(original, accessor).all().delete()
            getattr(original, accessor).set(old_qs, clear=True)
    else:
        class DummyObject(original.__class__):
            class Meta:
                abstract = True

            def save(self, **kwargs):
                pass

            def delete(self, **kwargs):
                pass

        for field in deffered_fields:
            accessor = field.get_accessor_name()
            old_qs = getattr(overlay, accessor).all()
            setattr(DummyObject, accessor, old_qs)

        DummyObject._meta = original.__class__._meta

        original.__class__ = DummyObject

    return original


def duplicate_object(original_object, changes=None):
    with update_index():
        copied_object = deepcopy(original_object)
        copied_object.pk = None

        if callable(changes):
            copied_object = changes(copied_object, original_object)

        AdminClass = admin.site._registry[original_object.__class__]

        for content_cls, admin_cls in AdminClass.inlines:
            pass

        copied_object.save()


def duplicate_page(original_page, page_changes=None):
    '''
        Takes a page and duplicates it as a child of the original's parent page.
        Expects to be passed the original page and an optional function
    '''
    from .admin import page_admin
    original_content = original_page.content

    with update_index():
        page = deepcopy(original_page)
        page.pk = None

        if callable(page_changes):
            page = page_changes(page, original_page)

        page.save()

        content = deepcopy(original_content)
        content.pk = None
        content.page = page
        content.save()

        # This doesn't copy m2m relations on the copied inline
        for content_cls, admin_cls in page_admin.content_inlines:
            if not isinstance(content, content_cls):
                continue

            model_cls = admin_cls.model
            fk = _get_foreign_key(Page, model_cls, fk_name=admin_cls.fk_name)

            related_items = model_cls.objects.filter(**{fk.name: original_page.pk}).distinct().all()
            for item in related_items:
                new_object = deepcopy(item)
                new_object.pk = None
                setattr(new_object, fk.name, page)
                new_object = overlay_obj(new_object, item, exclude=[fk.name, 'pk', 'id'], commit=True)
                new_object.save()

    return page


def overlay_page_obj(original_page, overlay_page, commit=False):
    '''
        A function that takes a page and overlay the fields and linked objects from a different page.
    '''
    from .admin import page_admin
    original_content = original_page.content
    page_fields_exclude = ['pk', 'id', 'version_for', 'left', 'right']
    content_fields_exclude = ['pk', 'id', 'page']

    checked_models = []
    related_fields = []

    def do_model_inline(cls):
        checked_models.append(cls.model)
        fk = _get_foreign_key(Page, cls.model, fk_name=cls.fk_name)

        return fk.related_query_name()

    for _, admin_cls in page_admin.content_inlines:

        if admin_cls.model in checked_models:
            continue

        related_fields.append(do_model_inline(admin_cls))

    # Overlay page fields
    overlay_obj(original_page, overlay_page, page_fields_exclude, related_fields, commit=commit)

    # Overlay page content fields
    overlay_obj(original_content, overlay_page.content, content_fields_exclude, [], commit=commit)

    return original_page


def publish_page(page):
    def page_changes(new_page, original_page):
        new_page.version_for = original_page
        new_page.left = None
        new_page.right = None
        return new_page

    if not page.version_for:
        return False

    live_page = page.version_for

    page_duplicate = duplicate_page(live_page, page_changes)
    overlay_page_obj(live_page, page, commit=True)

    # Update reversions
    # Version.objects.get_for_object(live_page).update(object_id=page_duplicate.pk)
    # Version.objects.get_for_object(page).update(object_id=live_page.pk)

    page.delete()

    return live_page


class PageTree:
    '''A page tree for when you can't trust `left` and `right` attributes'''

    def __init__(self, obj, **kwargs):
        self.root = PageNode(obj, **kwargs)
        self._pages_flat = []

    def get_pages_flat(self):
        if not self._pages_flat:
            self._pages_flat = [self.root.obj] + [node.obj for node in self.root.all_children]
        return self._pages_flat

    def set_page_attrs(self):
        self.root.set_page_attrs()

    def __str__(self):
        return f'{self.root}\n\n' + self.root.children_as_str()


class PageNode:
    '''A Node in an MPTT tree.
    - Recursively generates the tree from the given Page node
    - Ignores ``left`` and ``right`` attributes set on the page and works out its own

    Notes
    -----
    - Puts children in the order given by `page.child_set`
    - Most functions are recursive
    '''
    def __init__(self, obj, parent=None, db_alias=None, model=Page, child_filter=Q(is_canonical_page=True)):
        '''
        Parameters
        ----------
        obj
            The python object this node wraps.
        parent: PageNode
            The parent node (A value of ``None`` indicates this is the root node).
        db_alias
            Passed to the ``using`` method of querysets if present.
        model
            The type of page model this node wraps (defaults to cms.apps.pages.models.Page).
        child_filter: Q
            A Q object to additionally filter this node's children by.
        '''
        self.parent = parent
        self.left = None
        self.right = None
        self.leftattr = -1
        self.rightattr = -1
        self.obj = obj
        child_set = model.objects.using(db_alias) if db_alias else model.objects
        child_set = child_set.filter(parent=obj)
        if child_filter:
            child_set = child_set.filter(child_filter)
        self.children = [PageNode(p, parent=self, model=model, child_filter=child_filter) for p in list(child_set.all())]
        self.num_child_nodes = len(self.children) + sum([node.num_child_nodes for node in self.children])

        self.set_mptt_attrs(None, None)

    def set_page_attrs(self):
        self.obj.left = self.leftattr
        self.obj.right = self.rightattr
        for child in self.children:
            child.set_page_attrs()

    def set_mptt_attrs(self, left, right):
        self.left = left
        if left is None:
            if self.parent:
                self.leftattr = self.parent.leftattr + 1
            else:
                self.leftattr = 1
        else:
            self.leftattr = self.left.rightattr + 1

        self.right = right
        if self.children:
            l = None
            for i in range(0, len(self.children) - 1):
                child = self.children[i]
                r = self.children[i + 1]
                child.set_mptt_attrs(l, r)
                l = child

            self.children[-1].set_mptt_attrs(l, None)

            self.rightattr = self.children[-1].rightattr + 1
        else:
            self.rightattr = self.leftattr + 1

    @property
    def all_children(self):
        children = []
        if self.children:
            children += self.children
            for child in self.children:
                children += child.all_children
        return children

    def __str__(self):
        return f'<{self.leftattr} {self.obj} {self.rightattr}>'

    def __repr__(self):
        return str(self)

    def children_as_str(self):
        children = ' | '.join(map(lambda x: str(x), self.children))
        sub_children = ' | '.join([child.children_as_str() for child in self.children if child.children])
        return f'[{children}]' + ('\n\n' + sub_children if sub_children else '')


def mptt_fix():
    with publication_manager.select_published(False):
        homepage = Page.objects.get_homepage()
        tree = PageTree(homepage)
        tree.set_page_attrs()
        Page.objects.bulk_update(tree.get_pages_flat(), ['left', 'right'])
