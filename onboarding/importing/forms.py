import traceback

from horizon import exceptions, forms
from django.utils.translation import ugettext_lazy as _

from openstack_dashboard.dashboards.onboarding.importing import utils


class ImportForm(forms.SelfHandlingForm):
    name = forms.CharField(
        label=_("Stack name"),
        required=True,
        max_length=80,
        help_text=_("Stack name should be unique in the project"))

    importing = forms.FileField(
        label=_('OVA File'),
        help_text=_('A local importing to upload.'),
        widget=forms.FileInput(),
        required=False)

    def clean(self):
        cleaned_data = super(ImportForm, self).clean()
        return cleaned_data

    def handle(self, request, data):
        try:
            context={}
            if data:
                context['name'] = data.get("name", "")
                context['importing'] = data.get("importing", "")
                utils.importOVA(self, request, context)
            return True
        except Exception:
            print traceback.format_exc()
            exceptions.handle(request, _("Unable to add importing OVA"))
            return False