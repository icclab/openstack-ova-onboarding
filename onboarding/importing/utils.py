import traceback

import requests
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions


class OVA:
    def __init__(self, name, ova):
        self.name = name
        self.ova = ova


def importOVA(self, request, context):
    import_url = 'http://127.0.0.1:8006/'
    try:
        name = context.get('name')
        project_id = request.user.project_id
        token = request.user.token.id
        auth_url = request.user.endpoint
        region = request.user.services_region

        payload = {'stack_name': name, 'url': auth_url, 'token': token,
                   'project_id': project_id, 'region': region}
        requests.post(import_url + "api/upload", data=payload, files={'file': context.get('importing')})

    except:
        print "Exception inside utils.importOVA"
        print traceback.format_exc()
        exceptions.handle(self.request, _('Unable to importing OVA'))
        return []
