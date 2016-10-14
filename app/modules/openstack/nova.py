from app.modules.backend_logging import LOG
from novaclient import client


def get_smallest_flavor(matched_list):
    smallest_dict = matched_list
    smallest_flavor = None
    for i in range(3):
        smallest_value = None
        for flavor in smallest_dict:
            if not smallest_value:
                smallest_value = smallest_dict[flavor][i]
            if smallest_value > smallest_dict[flavor][i]:
                smallest_value = smallest_dict[flavor][i]
        temp_dict = {}
        for element in smallest_dict:
            if smallest_dict[element][i] == smallest_value:
                temp_dict[element] = smallest_dict[element]
                smallest_flavor = element
        smallest_dict = temp_dict
    return smallest_flavor


class NovaClient:

    def __init__(self, session, version, region):
        self.session = session
        self.version = version
        self.region = region

    def get_client(self):
        return client.Client(self.version, session=self.session, region_name=self.region)

    def get_flavors_list(self):
        return self.get_client().flavors.list()

    def get_status(self):
        status = False
        try:
            self.get_flavors_list()
            status = True
            LOG.info("Nova connection is established")
        except Exception as e:
            LOG.error("Couldn't connect to Nova client " + e)
        return status

    def get_flavor_map(self):
        flavor_map = {}
        for flavor in self.get_flavors_list():
            flavor_map[flavor.name] = [flavor.vcpus, flavor.ram, flavor.disk]
        return flavor_map

    def get_best_flavor(self, values):
        LOG.info("Getting the best flavor for virtual machine")
        best_list = self.get_flavor_map()
        for i in range(len(values)):
            initial_list = best_list
            best_list = {}
            for flavor in initial_list:
                if initial_list[flavor][i] >= values[i]:
                    best_list[flavor] = initial_list[flavor]
        if not best_list:
            LOG.error("No flavors matched")
        return get_smallest_flavor(best_list)






