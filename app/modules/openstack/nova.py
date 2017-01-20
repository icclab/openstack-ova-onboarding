from app.modules.backend_logging import LOG
from novaclient import client


def from_bytes_to_gb(size):
    return float(size)/1024/1024/1024


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

    def create_image_from_instance(self, instance_id, instance_name):
        return self.get_client().servers.create_image(instance_id, instance_name)

    def get_instance_by_id(self, instance_id):
        return self.get_client().servers.get(instance_id)

    def get_client(self):
        return client.Client(self.version, session=self.session, region_name=self.region)

    def get_flavors_list(self):
        return self.get_client().flavors.list()

    def get_flavor(self, name="", id=""):
        for flavor in self.get_flavors_list():
            if (flavor.name == name) or (flavor.id == id):
                return flavor

    def get_security_rules(self, nova_instance):
        unique_groups = []
        for security_group in nova_instance.security_groups:
            if security_group not in unique_groups:
                unique_groups.append(security_group)
        rules = []
        for unique_group in unique_groups:
            for group in self.get_client().security_groups.list():
                if group.name == unique_group['name']:
                    for rule in group.rules:
                        if rule['ip_protocol'] in ['tcp', 'udp']:
                            for port in range(rule['from_port'], rule['to_port'] + 1):
                                rules.append({'port': port,
                                              'ip_protocol': rule['ip_protocol']})
                    break
        return [dict(t) for t in set([tuple(rule.items()) for rule in rules])]

    def check_quota(self, vms):
        quota = self.get_project_quota()
        available_resources = {"availableInstances": quota["maxTotalInstances"] - quota["totalInstancesUsed"],
                               "availableCores": quota["maxTotalCores"] - quota["totalCoresUsed"],
                               "availableRAM": quota["maxTotalRAMSize"] - quota["totalRAMUsed"]}
        for vm in vms:
            flavor = self.get_flavor(
                name=self.get_best_flavor([int(vm.cpu), int(vm.ram), from_bytes_to_gb(vm.disk)]
                                          )
            )
            available_resources["availableInstances"] -= 1
            available_resources["availableCores"] -= flavor.vcpus
            available_resources["availableRAM"] -= flavor.ram
        for key in available_resources:
            if available_resources[key] < 0:
                message = "Not enough resources to create all virtual machines, expected quota after migration:" + \
                          str(available_resources)
                return False, message
        message = "expected quota after migration:" + str(available_resources)
        return True, message

    def get_project_quota(self):
        return self.get_client().limits.get()._info['absolute']

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






