from app.modules.backend_logging import LOG
from glanceclient import client


class GlanceClient:

    def __init__(self, version, session, region):
        self.version = version
        self.session = session
        self.region = region

    def get_client(self):
        if self.region:
            return client.Client(self.version, session=self.session, region_name=self.region)
        else:
            return client.Client(self.version, session=self.session)

    def get_image_list(self):
        LOG.info("Fetching image list ...")
        return self.get_client().images.list()

    def get_status(self):
        status = False
        try:
            self.get_image_list()
            status = True
            LOG.info("Glance connection is established")
        except Exception as e:
            LOG.error("Couldn't connect to Glance client " + e)
        return status

    def upload_image(self, name, image_location):
        LOG.info("Uploading "+name+" image to glance ...")
        image = self.get_client().images.create(name=name, disk_format='vmdk', container_format='bare')
        self.get_client().images.upload(image.id, open(image_location))
        return image.id
