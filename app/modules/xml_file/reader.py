def get_text(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)


class VM:
    def __init__(self, name, cpu, ram, image, network):
        self.name = name
        self.cpu = cpu
        self.ram = ram
        self.image = image
        self.network = network


class GeneratedVM:
    def __init__(self, name, flavor, image, networks, sec_groups):
        self.name = name
        self.flavor = flavor
        self.image = image
        self.networks = networks
        self.sec_groups = sec_groups
