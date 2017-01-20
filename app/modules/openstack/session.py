import abc

from keystoneauth1 import session
from keystoneauth1 import loading
from keystoneauth1.identity import v2
from keystoneauth1.identity import v3


class BaseSession:
    def __init__(self, auth_url, tenant_id):
        self.auth_url = auth_url
        self.tenant_id = tenant_id
        self._auth = None
        self._session = None
        self._token = None

    @abc.abstractmethod
    def auth(self):
        """Method authentication"""
        return

    @property
    def session(self):
        return session.Session(auth=self.auth)

    def get_endpoint(self, service_name, region):
        access = self.auth.get_access(self.session)
        for service in access.service_catalog.catalog:
            if service["name"] == service_name:
                for service_endpoint in service["endpoints"]:
                    if service_endpoint["region"] == region:
                        if "publicURL" in service_endpoint:
                            return service_endpoint["publicURL"]
                        elif "url" in service_endpoint:
                            return service_endpoint["url"]


class TokenSession(BaseSession):
    def __init__(self, auth_url, token, tenant_id):
        BaseSession.__init__(self, auth_url, tenant_id)
        self.token = token

    @property
    def auth(self):
        if 'v2' in self.auth_url:
            token = v2.Token(token=self.token, auth_url=self.auth_url, tenant_id=self.tenant_id)
            return token
#        if 'v3' in self.auth_url:
        else:
            token = v3.TokenMethod(token=self.token)
            return v3.Auth(auth_url=self.auth_url,
                           auth_methods=[token],
                           project_id=self.tenant_id
                           )


class LogInSession(BaseSession):
    def __init__(self, auth_url, username, password, tenant_id):
        BaseSession.__init__(self, auth_url, tenant_id)
        self.username = username
        self.password = password

    @property
    def token(self):
        return self.auth.get_token(self.session)

    @property
    def auth(self):
        loader = loading.get_plugin_loader('password')
        auth = loader.load_from_options(
            auth_url=self.auth_url,
            username=self.username,
            password=self.password,
            project_id=self.tenant_id)
        return auth


def get_valid_session(openstack):
    if 'token' in openstack:
        valid_session = TokenSession(auth_url=openstack['url'],
                                     token=openstack['token'],
                                     tenant_id=openstack['project_id'], )
    elif 'username' in openstack and 'password' in openstack:
        valid_session = LogInSession(auth_url=openstack['url'],
                                     username=openstack['username'],
                                     password=openstack['password'],
                                     tenant_id=openstack['project_id'], )
    else:
        raise Exception("Couldn't authorised. Please provide username/password or token")

    return valid_session
