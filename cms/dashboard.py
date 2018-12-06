from django.utils.translation import ugettext_lazy as _
from jet.dashboard import modules
from jet.dashboard.dashboard import Dashboard, AppIndexDashboard

from .dashboard_modules import SiteMap


class OSMDashboard(Dashboard):
    columns = 3

    def init_with_context(self, context):
        self.available_children.append(modules.AppList)
        self.available_children.append(modules.ModelList)
        self.available_children.append(modules.RecentActions)
        self.available_children.append(SiteMap)
        self.children.append(modules.AppList(
            _('Apps'),
            column=0,
        ))
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            column=1,
        ))
        self.children.append(SiteMap(
            _('Sitemap'),
            column=2,
        ))
