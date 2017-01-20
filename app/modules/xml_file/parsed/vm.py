from app.modules.xml_file.reader import get_text

from app import app


def generate_template(vm_list):
    yaml_dict = {"heat_template_version": app.config["HEAT_VERSION"],
                 "description": "ova",
                 "resources": {}
                 }
    list_of_common_networks={}
    cidr = app.config["CIDR"]
    public_net = app.config["PUBLIC_NET"]
    used_names = []

    def get_valid_name(name):
        i=0
        while name in used_names:
            name += '_' + str(i)
            i +=1
        used_names.append(name)
        return str(name)

    for vm in vm_list:
        vm_name = get_valid_name(vm.name)
        yaml_dict["resources"][vm_name] = {"type": "OS::Nova::Server",
                                                   "properties":
                                                      {"name": str(vm.name),
                                                       "image": str(vm.image),
                                                       "flavor": str(vm.flavor),
                                                       "networks": []
                                                     }
                                                }
        for network in vm.networks:
            network_name = get_valid_name(network)
            port_name = get_valid_name(vm.name+"_"+network+"_port")
            if network not in list_of_common_networks:
                list_of_common_networks[network] = network_name
                yaml_dict["resources"][network_name] = {"type": "OS::Neutron::Net",
                                                        "properties":
                                                            {"name": str(network)
                                                             }
                                                        }
                yaml_dict["resources"][network_name + "_subnet"] = {"type": "OS::Neutron::Subnet",
                                                                  "properties":
                                                                      {"network_id": {
                                                                          "get_resource": network_name
                                                                      },
                                                                          "cidr": str(cidr)
                                                                      }
                                                                  }
            yaml_dict["resources"][port_name] = {"type": "OS::Neutron::Port",
                                                                        "properties":
                                                                            {"network_id": {
                                                                                "get_resource":
                                                                                    list_of_common_networks[network]
                                                                            },
                                                                                "fixed_ips": [{
                                                                                    "subnet_id": {
                                                                                        "get_resource":
                                                                                            str(list_of_common_networks[
                                                                                                network] + "_subnet")
                                                                                    }
                                                                                }]
                                                                            }
                                                                        }
            yaml_dict["resources"][vm_name]["properties"]["networks"].append({"port": {"get_resource":
                                                                                            port_name
                                                                                            }
                                                                                   })
        if vm.sec_groups:
            public_port = get_valid_name(vm.name+"_"+public_net+"_port")
            group = vm.name+"_"+public_net+"_port"+"_security_group"
            security_group = get_valid_name(group)
            yaml_dict["resources"][public_port] = {"type": "OS::Neutron::Port",
                                            "properties":
                                                {
                                                    "network_id": public_net,
                                                    "security_groups": []
                                                }
                                            }
            yaml_dict["resources"][vm_name]["properties"]["networks"].append({"port": {"get_resource": public_port
                                                                                            }
                                                                                   })
            yaml_dict["resources"][security_group] = {"type": "OS::Neutron::SecurityGroup",
                                                      "properties":
                                                          {
                                                              "description": "TODO",
                                                              "name": str(group),
                                                              "rules": []
                                                          }
                                                      }
            tcp = False
            for group in vm.sec_groups:
                if tcp:
                    protocol = "tcp"
                else:
                    protocol = "udp"

                def add_rule(min, max):
                    yaml_dict["resources"][security_group]["properties"]["rules"].append(
                        {"remote_ip_prefix": "0.0.0.0/0",
                         "protocol": protocol,
                         "port_range_min": str(min),
                         "port_range_max": str(max)
                         }
                    )
                tcp = not tcp
                if group:
                    need_min = False
                    min_port, max_port = min(group), min(group)
                    for port in sorted(group):
                        if need_min:
                            min_port = port
                            need_min = False
                        if port - max_port >= 2:
                            add_rule(min_port, max_port)
                            need_min = True
                        else:
                            max_port = port
                    add_rule(min_port, max_port)

            yaml_dict["resources"][public_port]["properties"]["security_groups"].append({"get_resource": security_group})

    return yaml_dict


class ParsedVM:
    def __init__(self, data):
        self.data = data

    def get_meter_by_description(self, description):
        for element in self.data.getElementsByTagName("Item"):
            if get_text(element.getElementsByTagName("rasd:Description")[0].childNodes) == description:
                return get_text(element.getElementsByTagName("rasd:VirtualQuantity")[0].childNodes)

    def get_name(self):
        return get_text(self.data.getElementsByTagName("vssd:VirtualSystemIdentifier")[0].childNodes)

    def get_memory(self):
        return self.get_meter_by_description("Memory Size")

    def get_cpu(self):
        try:
            return self.get_meter_by_description("Number of virtual CPUs")
        except:
            return self.get_meter_by_description("Number of Virtual CPUs")

    def get_image(self):
        try:
            return get_text(self.data.getElementsByTagName("sasd:HostResource")[0].childNodes)
        except:
            return get_text(self.data.getElementsByTagName("rasd:HostResource")[0].childNodes)

    def get_network(self):
        network_dict = {"internal_network": [], "NAT": []}
        for network in self.data.getElementsByTagName("Adapter"):
            if network.getAttribute("enabled") == "true":
                if network.getElementsByTagName("DisabledModes"):
                    element = network.getElementsByTagName("DisabledModes")[0]
                    network.removeChild(element)
                if network.getElementsByTagName("InternalNetwork"):
                    network_dict["internal_network"].append(network.getElementsByTagName("InternalNetwork")[0].getAttribute("name"))
                if network.getElementsByTagName("NAT"):
                    network_dict["NAT"] = [[], []]
                    for forward in network.getElementsByTagName("Forwarding"):
                        network_dict["NAT"][int(forward.getAttribute("proto"))].append(int(forward.getAttribute("guestport")))
        return network_dict
