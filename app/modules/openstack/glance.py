from app.modules.backend_logging import LOG
from glanceclient import client


class GlanceClient:

    def __init__(self, version, session, region):
        self.version = version
        self.session = session
        self.region = region

    def get_client(self):
        return client.Client(self.version, session=self.session)

    def get_image_list(self):
        LOG.info("Fetching image list ...")
        return self.get_client().images.list()

    def get_image_data(self, image_id):
        return self.get_client().images.data(image_id)

    def get_image(self, image_id):
        return self.get_client().images.get(image_id)

    def remove_image(self, image_id):
        return self.get_client().images.delete(image_id)

    def remove_list_of_images(self, my_list):
        for image in my_list:
            self.remove_image(image)

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
        try:
            name = str(name).split('.')[0]
        except:
            pass
        LOG.info("Uploading "+name+" image to glance ...")
        image = self.get_client().images.create(name=name, disk_format='vmdk', container_format='bare')
        self.get_client().images.upload(image.id, open(image_location))
        return image.id
