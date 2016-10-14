from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs

from openstack_dashboard import api
from openstack_dashboard.dashboards.onboarding.ova import tables


class StackTab(tabs.TableTab):
    name = _("Stacks Tab")
    slug = "stacks_tab"
    table_classes = (tables.StacksTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = False

    def has_more_data(self, table):
        return self._has_more

    def get_ova_data(self):
        try:
            marker = self.request.GET.get(
                tables.StacksTable._meta.pagination_param, None)

            stacks, self._has_more, self._has_prev_data = api.heat.stacks_list(
                self.request, marker=marker, paginate=True)

            ova_stacks = []
            for stack in stacks:
                if api.heat.stack_get(request=self.request, stack_id=stack.id).description == "ova":
                    ova_stacks.append(stack)

            return ova_stacks
        except Exception:
            self._has_more = False
            error_message = _('Unable to get stacks')
            exceptions.handle(self.request, error_message)

            return []


class MypanelTabs(tabs.TabGroup):
    slug = "mypanel_tabs"
    tabs = (StackTab,)
    sticky = True