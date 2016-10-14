from keystoneauth1 import session
from keystoneauth1.identity import v3


class Session:
    def __init__(self, auth_url, token, tenant_id):
        self.auth_url = auth_url
        self.tenant_id = tenant_id
        self.token = token
        self._auth = None
        self._session = None

    @property
    def auth(self):
        token = v3.TokenMethod(token=self.token)
        return v3.Auth(auth_url=self.auth_url,
                       auth_methods=[token],
                       project_id=self.tenant_id
                       )

    @property
    def session(self):
        return session.Session(auth=self.auth)

    def get_endpoint(self, service_name, region):
        access = self.auth.get_access(self.session)
        for service in access.service_catalog.catalog:
            if service["name"] == service_name:
                for service_endpoint in service["endpoints"]:
                    if service_endpoint["region"] == region:
                        return service_endpoint["url"]
