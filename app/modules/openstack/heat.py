from app.modules.backend_logging import LOG
from heatclient import client


class HeatClient:
    def __init__(self, version, endpoint, token):
        self.version = version
        self.endpoint = endpoint
        self.token = token

    def get_client(self):
        return client.Client(self.version, endpoint=self.endpoint, token=self.token)

    def get_stack_list(self):
        return self.get_client().stacks.list()

    def get_status(self):
        status = False
        try:
            self.get_stack_list()
            status = True
            LOG.info("Heat connection is established")
        except Exception as e:
            LOG.error("Couldn't connect to Heat client " + e)
        return status

    def create_stack(self, name,  body):
        LOG.info("Uploading template file to heat endpoint")
        self.get_client().stacks.create(stack_name=name,
                                        template=body)
        LOG.info("Template is uploaded successfully")
