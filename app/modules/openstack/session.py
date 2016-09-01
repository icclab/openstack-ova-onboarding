from keystoneauth1 import loading
from keystoneauth1 import session


class Session:
    def __init__(self, auth_url, username, password, tenant_name):
        self.auth_url = auth_url
        self.username = username
        self.password = password
        self.tenant_name = tenant_name
        self._auth = None
        self._session = None
        self._token = None

    @property
    def auth(self):
        loader = loading.get_plugin_loader('password')
        auth = loader.load_from_options(
            auth_url=self.auth_url,
            username=self.username,
            password=self.password,
            tenant_name=self.tenant_name)
        return auth

    @property
    def session(self):
        return session.Session(auth=self.auth)

    @property
    def token(self):

        return self.auth.get_token(self.session)

    def get_endpoint(self, service_name, region):
        access = self.auth.get_access(self.session)
        for service in access.service_catalog.catalog:
            if service["name"] == service_name:
                for service_endpoint in service["endpoints"]:
                    if service_endpoint["region"] == region:
                        return service_endpoint["publicURL"]
                return service["endpoints"][0]["publicURL"]
