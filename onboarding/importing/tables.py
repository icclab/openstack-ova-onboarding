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

from django.core import urlresolvers
from django.http import Http404  # noqa
from django.template.defaultfilters import title  # noqa
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import messages
from horizon import tables
from horizon.utils import filters

from heatclient import exc

from openstack_dashboard import api
from openstack_dashboard.dashboards.project.stacks import mappings


class ImportOVA(tables.LinkAction):
    name = "importing"
    verbose_name = _("Import OVA")
    url = "horizon:onboarding:importing:importing"
    classes = ("btn-launch", "ajax-modal")
    icon = "plus"


class CheckStack(tables.BatchAction):
    name = "check"
    verbose_name = _("Check Application")
    policy_rules = (("orchestration", "actions:action"),)
    icon = "check-square"

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Check Application",
            u"Check Application",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Checked Application",
            u"Checked Application",
            count
        )

    def action(self, request, stack_id):
        api.heat.action_check(request, stack_id)


class SuspendStack(tables.BatchAction):
    name = "suspend"
    verbose_name = _("Suspend Application")
    policy_rules = (("orchestration", "actions:action"),)
    icon = "pause"

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Suspend Application",
            u"Suspend Application",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Suspended Application",
            u"Suspended Application",
            count
        )

    def action(self, request, stack_id):
        api.heat.action_suspend(request, stack_id)


class ResumeStack(tables.BatchAction):
    name = "resume"
    verbose_name = _("Resume Application")
    policy_rules = (("orchestration", "actions:action"),)
    icon = "play"

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Resume Application",
            u"Resume Application",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Resumed Application",
            u"Resumed Application",
            count
        )

    def action(self, request, stack_id):
        api.heat.action_resume(request, stack_id)


class DeleteStack(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete OVA",
            u"Delete OVA",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted OVA",
            u"Deleted OVA",
            count
        )

    policy_rules = (("orchestration", "stacks:delete"),)

    def delete(self, request, stack_id):
        api.heat.stack_delete(request, stack_id)

    def allowed(self, request, stack):
        if stack is not None:
            return stack.stack_status != 'DELETE_COMPLETE'
        return True


class StacksUpdateRow(tables.Row):
    ajax = True

    def can_be_selected(self, datum):
        return datum.stack_status != 'DELETE_COMPLETE'

    def get_data(self, request, stack_id):
        try:
            stack = api.heat.stack_get(request, stack_id)
            if stack.stack_status == 'DELETE_COMPLETE':
                # returning 404 to the ajax call removes the
                # row from the table on the ui
                raise Http404
            return stack
        except Http404:
            raise
        except Exception as e:
            messages.error(request, e)
            raise


class StacksFilterAction(tables.FilterAction):

    def filter(self, table, stacks, filter_string):
        """Naive case-insensitive search."""
        query = filter_string.lower()
        return [stack for stack in stacks
                if query in stack.name.lower()]


class StacksTable(tables.DataTable):
    STATUS_CHOICES = (
        ("Complete", True),
        ("Failed", False),
    )
    STACK_STATUS_DISPLAY_CHOICES = (
        ("init_in_progress", pgettext_lazy("current status of application",
                                           u"Init In Progress")),
        ("init_complete", pgettext_lazy("current status of application",
                                        u"Init Complete")),
        ("init_failed", pgettext_lazy("current status of application",
                                      u"Init Failed")),
        ("create_in_progress", pgettext_lazy("current status of application",
                                             u"Create In Progress")),
        ("create_complete", pgettext_lazy("current status of application",
                                          u"Create Complete")),
        ("create_failed", pgettext_lazy("current status of application",
                                        u"Create Failed")),
        ("delete_in_progress", pgettext_lazy("current status of application",
                                             u"Delete In Progress")),
        ("delete_complete", pgettext_lazy("current status of application",
                                          u"Delete Complete")),
        ("delete_failed", pgettext_lazy("current status of application",
                                        u"Delete Failed")),
        ("update_in_progress", pgettext_lazy("current status of application",
                                             u"Update In Progress")),
        ("update_complete", pgettext_lazy("current status of application",
                                          u"Update Complete")),
        ("update_failed", pgettext_lazy("current status of application",
                                        u"Update Failed")),
        ("rollback_in_progress", pgettext_lazy("current status of application",
                                               u"Rollback In Progress")),
        ("rollback_complete", pgettext_lazy("current status of application",
                                            u"Rollback Complete")),
        ("rollback_failed", pgettext_lazy("current status of application",
                                          u"Rollback Failed")),
        ("suspend_in_progress", pgettext_lazy("current status of application",
                                              u"Suspend In Progress")),
        ("suspend_complete", pgettext_lazy("current status of application",
                                           u"Suspend Complete")),
        ("suspend_failed", pgettext_lazy("current status of application",
                                         u"Suspend Failed")),
        ("resume_in_progress", pgettext_lazy("current status of application",
                                             u"Resume In Progress")),
        ("resume_complete", pgettext_lazy("current status of application",
                                          u"Resume Complete")),
        ("resume_failed", pgettext_lazy("current status of application",
                                        u"Resume Failed")),
        ("adopt_in_progress", pgettext_lazy("current status of application",
                                            u"Adopt In Progress")),
        ("adopt_complete", pgettext_lazy("current status of application",
                                         u"Adopt Complete")),
        ("adopt_failed", pgettext_lazy("current status of application",
                                       u"Adopt Failed")),
        ("snapshot_in_progress", pgettext_lazy("current status of application",
                                               u"Snapshot In Progress")),
        ("snapshot_complete", pgettext_lazy("current status of application",
                                            u"Snapshot Complete")),
        ("snapshot_failed", pgettext_lazy("current status of application",
                                          u"Snapshot Failed")),
        ("check_in_progress", pgettext_lazy("current status of application",
                                            u"Check In Progress")),
        ("check_complete", pgettext_lazy("current status of application",
                                         u"Check Complete")),
        ("check_failed", pgettext_lazy("current status of application",
                                       u"Check Failed")),
    )
    name = tables.Column("stack_name",
                         verbose_name=_("OVA Name"),
                         link="horizon:project:stacks:detail",)
    created = tables.Column("creation_time",
                            verbose_name=_("Created"),
                            filters=(filters.parse_isotime,
                                     filters.timesince_or_never))
    updated = tables.Column("updated_time",
                            verbose_name=_("Updated"),
                            filters=(filters.parse_isotime,
                                     filters.timesince_or_never))
    status = tables.Column("status",
                           hidden=True,
                           status=True,
                           status_choices=STATUS_CHOICES)

    stack_status = tables.Column("stack_status",
                                 verbose_name=_("Status"),
                                 display_choices=STACK_STATUS_DISPLAY_CHOICES)

    def get_object_display(self, stack):
        return stack.stack_name

    class Meta(object):
        name = "importing"
        verbose_name = _("Import")
        pagination_param = 'stack_marker'
        status_columns = ["status", ]
        row_class = StacksUpdateRow
        table_actions_menu = (CheckStack,
                              SuspendStack,
                              ResumeStack,)
        table_actions = (ImportOVA,
                         DeleteStack,
                         StacksFilterAction,)
        row_actions = (CheckStack,
                       SuspendStack,
                       ResumeStack,
                       DeleteStack,)


def get_resource_url(obj):
    if obj.physical_resource_id == obj.stack_id:
        return None
    return urlresolvers.reverse('horizon:project:stacks:resource',
                                args=(obj.stack_id, obj.resource_name))


class EventsTable(tables.DataTable):

    logical_resource = tables.Column('resource_name',
                                     verbose_name=_("Stack Resource"),
                                     link=get_resource_url)
    physical_resource = tables.Column('physical_resource_id',
                                      verbose_name=_("Resource"))
    timestamp = tables.Column('event_time',
                              verbose_name=_("Time Since Event"),
                              filters=(filters.parse_isotime,
                                       filters.timesince_or_never))
    status = tables.Column("resource_status",
                           filters=(title, filters.replace_underscores),
                           verbose_name=_("Status"),)

    statusreason = tables.Column("resource_status_reason",
                                 verbose_name=_("Status Reason"),)

    class Meta(object):
        name = "events"
        verbose_name = _("Stack Events")


class ResourcesUpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, resource_name):
        try:
            stack = self.table.stack
            stack_identifier = '%s/%s' % (stack.stack_name, stack.id)
            return api.heat.resource_get(
                request, stack_identifier, resource_name)
        except exc.HTTPNotFound:
            # returning 404 to the ajax call removes the
            # row from the table on the ui
            raise Http404
        except Exception as e:
            messages.error(request, e)


class ResourcesTable(tables.DataTable):
    class StatusColumn(tables.Column):
        def get_raw_data(self, datum):
            return datum.resource_status.partition("_")[2]

    STATUS_CHOICES = (
        ("Complete", True),
        ("Failed", False),
    )
    STATUS_DISPLAY_CHOICES = StacksTable.STACK_STATUS_DISPLAY_CHOICES

    logical_resource = tables.Column('resource_name',
                                     verbose_name=_("Stack Resource"),
                                     link=get_resource_url)
    physical_resource = tables.Column('physical_resource_id',
                                      verbose_name=_("Resource"),
                                      link=mappings.resource_to_url)
    resource_type = tables.Column("resource_type",
                                  verbose_name=_("Stack Resource Type"),)
    updated_time = tables.Column('updated_time',
                                 verbose_name=_("Date Updated"),
                                 filters=(filters.parse_isotime,
                                          filters.timesince_or_never))
    status = tables.Column("resource_status",
                           verbose_name=_("Status"),
                           display_choices=STATUS_DISPLAY_CHOICES)

    statusreason = tables.Column("resource_status_reason",
                                 verbose_name=_("Status Reason"),)

    status_hidden = StatusColumn("status",
                                 hidden=True,
                                 status=True,
                                 status_choices=STATUS_CHOICES)

    def __init__(self, request, data=None,
                 needs_form_wrapper=None, **kwargs):
        super(ResourcesTable, self).__init__(
            request, data, needs_form_wrapper, **kwargs)
        self.stack = kwargs['stack']

    def get_object_id(self, datum):
        return datum.resource_name

    class Meta(object):
        name = "resources"
        verbose_name = _("Stack Resources")
        status_columns = ["status_hidden", ]
        row_class = ResourcesUpdateRow
