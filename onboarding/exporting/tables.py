# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging

from django import template
from django.template.defaultfilters import title  # noqa
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from horizon import tables
from horizon.utils import filters
import utils

LOG = logging.getLogger(__name__)

POWER_STATES = {
    0: "NO STATE",
    1: "RUNNING",
    2: "BLOCKED",
    3: "PAUSED",
    4: "SHUTDOWN",
    5: "SHUTOFF",
    6: "CRASHED",
    7: "SUSPENDED",
    8: "FAILED",
    9: "BUILDING",
}


def is_deleting(instance):
    task_state = getattr(instance, "OS-EXT-STS:task_state", None)
    if not task_state:
        return False
    return task_state.lower() == "deleting"


class ExportInstance(tables.BatchAction):
    name = "export"
    verbose_name = _("Export Instances")
    url = "horizon:onboarding:exporting:exporting"
    classes = ("ajax-modal", "btn-launch")
    icon = "cloud-upload"
    ajax = True

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Export Applications",
            u"Export Applications",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Exported Applications",
            u"Exported Applications",
            count
        )

    def allowed(self, request, instance=None):
        """Allow delete action if instance is in error state or not currently
        being deleted.
        """
        error_state = False
        if instance:
            error_state = (instance.status == 'ERROR')
        return error_state or not is_deleting(instance)

    def handle(self, table, request, obj_ids):
        utils.exporting(self, request, obj_ids)


def get_ips(instance):
    template_name = 'project/instances/_instance_ips.html'
    ip_groups = {}

    for ip_group, addresses in instance.addresses.items():
        ip_groups[ip_group] = {}
        ip_groups[ip_group]["floating"] = []
        ip_groups[ip_group]["non_floating"] = []

        for address in addresses:
            if ('OS-EXT-IPS:type' in address and
               address['OS-EXT-IPS:type'] == "floating"):
                ip_groups[ip_group]["floating"].append(address)
            else:
                ip_groups[ip_group]["non_floating"].append(address)

    context = {
        "ip_groups": ip_groups,
    }
    return template.loader.render_to_string(template_name, context)


def get_power_state(instance):
    return POWER_STATES.get(getattr(instance, "OS-EXT-STS:power_state", 0), '')


class InstancesTable(tables.DataTable):
    TASK_STATUS_CHOICES = (
        (None, True),
        ("none", True)
    )
    STATUS_CHOICES = (
        ("active", True),
        ("shutoff", True),
        ("suspended", True),
        ("paused", True),
        ("error", False),
        ("rescue", True),
        ("shelved", True),
        ("shelved_offloaded", True),
    )
    name = tables.WrappingColumn("name",
                                 link="horizon:project:instances:detail",
                                 verbose_name=_("Instance Name"))
    ip = tables.Column(get_ips,
                       verbose_name=_("IP Address"),
                       attrs={'data-type': "ip"})
    status = tables.Column("status",
                           filters=(title, filters.replace_underscores),
                           verbose_name=_("Status"),
                           status=True,
                           status_choices=STATUS_CHOICES,
                           )
    az = tables.Column("availability_zone",
                       verbose_name=_("Availability Zone"))

    state = tables.Column(get_power_state,
                          filters=(title, filters.replace_underscores),
                          verbose_name=_("Power State"),
                          )
    created = tables.Column("created",
                            verbose_name=_("Time since created"),
                            filters=(filters.parse_isotime,
                                     filters.timesince_sortable),
                            attrs={'data-type': 'timesince'})

    class Meta(object):
        name = "exporting"
        verbose_name = _("Exporting")
        status_columns = ["status"]
        launch_actions = ()
        table_actions = launch_actions + (ExportInstance, )



