import traceback

import requests
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions


def exporting(self, request, objects):
    export_url = 'http://127.0.0.1:8006/'
    try:
        project_id = request.user.project_id
        token = request.user.token.id
        auth_url = request.user.endpoint
        region = request.user.services_region

        payload = {'url': auth_url, 'token': token,
                   'project_id': project_id, 'region': region, 'instance_id': objects}
        requests.post(export_url + "api/generate", data=payload)

    except:
        print "Exception inside utils.exporting"
        print traceback.format_exc()
        exceptions.handle(self.request, _('Unable to export'))
        return []
