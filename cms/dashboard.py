from jet.dashboard import modules
from jet.dashboard.dashboard import Dashboard, AppIndexDashboard

from .dashboard_modules import SiteMap


class OSMDashboard(Dashboard):
    columns = 3

    def init_with_context(self, context):
        self.children.append(modules.AppList)
        self.children.append(modules.ModelList)
        self.children.append(modules.RecentActions)
        self.children.append(SiteMap)
