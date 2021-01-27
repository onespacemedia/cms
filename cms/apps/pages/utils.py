from .models import Page
from cms.models.managers import publication_manager


class PageTree:
    '''
        A page tree for when you can't trust 'left' and 'right' attributes
    '''
    def __init__(self, page):
        self.root = PageNode(page)
        self._pages_flat = []

    def get_pages_flat(self):
        if not self._pages_flat:
            self._pages_flat = [self.root.page] + [node.page for node in self.root.all_children]
        return self._pages_flat

    def set_page_attrs(self):
        self.root.set_page_attrs()

    def __str__(self):
        return f'{self.root}\n\n' + self.root.children_as_str()


class PageNode:
    '''
        Recursively generates a tree from the given Page node.
        - Ignores 'left' and 'right' attributes set on the page and works out its own
        - Puts children in the order given by page.child_set
        - Most functions are recursive
    '''
    def __init__(self, page, parent=None):
        self.parent = parent
        self.left = None
        self.right = None
        self.leftattr = -1
        self.rightattr = -1
        self.page = page
        self.children = [PageNode(p, parent=self) for p in page.child_set.filter(is_content_object=False)]
        self.num_child_nodes = len(self.children) + sum([node.num_child_nodes for node in self.children])

        self.set_mptt_attrs(None, None)

    def set_page_attrs(self):
        self.page.left = self.leftattr
        self.page.right = self.rightattr
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
        return f'<{self.leftattr} {self.page} {self.rightattr}>'

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
        for page in tree.get_pages_flat():
            page.save()
