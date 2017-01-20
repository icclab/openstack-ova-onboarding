# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import forms
from horizon import tabs

from openstack_dashboard.dashboards.onboarding.importing import tabs as my_tabs
from openstack_dashboard.dashboards.onboarding.importing.forms import ImportForm


class OvaIndexView(tabs.TabbedTableView):
    # A very simple class-based view...
    tab_group_class = my_tabs.MypanelTabs
    template_name = 'onboarding/importing/index.html'

    def get_data(self, request, context, *args, **kwargs):
        # Add data to the context here...
        return context


class ImportOVAView (forms.ModalFormView):
    template_name = 'onboarding/importing/importing.html'
    modal_header = _("Import OVA")
    form_id = "importing"
    form_class = ImportForm
    submit_label = _("Import")
    submit_url = reverse_lazy("horizon:onboarding:importing:importing")
    success_url = reverse_lazy('horizon:onboarding:importing:index')
    page_title = _("Import OVA")

    def get_form_kwargs(self):
        kwargs = super(ImportOVAView, self).get_form_kwargs()

        return kwargs
