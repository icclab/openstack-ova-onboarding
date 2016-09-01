from app.modules.xml_file.reader import get_text

from app import app


def generate_template(vm_list):
    yaml_dict = {"heat_template_version": "2015-04-30",
                 "description": "here",
                 "resources": {}
                 }
    list_of_common_networks=[]
    cidr = app.config["CIDR"]
    public_net = app.config["PUBLIC_NET"]
    for vm in vm_list:
        yaml_dict["resources"][str(vm.name)] = {"type": "OS::Nova::Server",
                                                "properties":
                                                    {"name": str(vm.name),
                                                     "image": str(vm.image),
                                                     "flavor": str(vm.flavor),
                                                     "networks": []
                                                     }
                                                }

        for network in vm.networks:
            if network not in list_of_common_networks:
                yaml_dict["resources"][str(network)] = {"type": "OS::Neutron::Net",
                                                        "properties":
                                                            {"name": str(network)
                                                             }
                                                        }
                yaml_dict["resources"][str(network)+"_subnet"] = {"type": "OS::Neutron::Subnet",
                                                                  "properties":
                                                                      {"network_id": {
                                                                          "get_resource": str(network)
                                                                      },
                                                                          "cidr": str(cidr)
                                                                      }
                                                                  }
            yaml_dict["resources"][str(vm.name+"_"+network+"_port")] = {"type": "OS::Neutron::Port",
                                                                        "properties":
                                                                            {"network_id": {
                                                                                "get_resource": str(network)
                                                                            },
                                                                                "fixed_ips": [{
                                                                                    "subnet_id": {
                                                                                        "get_resource":
                                                                                            str(network) + "_subnet"
                                                                                    }
                                                                                }]
                                                                            }
                                                                        }
            yaml_dict["resources"][str(vm.name)]["properties"]["networks"].append({"port": {"get_resource":
                                                                                            str(vm.name+"_"+network+"_port")
                                                                                            }
                                                                                   })
        if vm.sec_groups:
            port = str(vm.name+"_"+public_net+"_port")
            yaml_dict["resources"][port] = {"type": "OS::Neutron::Port",
                                            "properties":
                                                {
                                                    "network_id": str(public_net),
                                                    "security_groups": []
                                                }
                                            }
            yaml_dict["resources"][str(vm.name)]["properties"]["networks"].append({"port": {"get_resource": port
                                                                                            }
                                                                                   })
            security_group = str(vm.name+"_"+public_net+"_port"+"_security_group")
            yaml_dict["resources"][security_group] = {"type": "OS::Neutron::SecurityGroup",
                                                      "properties":
                                                          {
                                                              "description": "TODO",
                                                              "name": security_group,
                                                              "rules": []
                                                          }
                                                      }
            for group in vm.sec_groups:
                if group["protocol"] == "1":
                    protocol = "tcp"
                else:
                    protocol = "udp"

                yaml_dict["resources"][security_group]["properties"]["rules"].append(
                    {"remote_ip_prefix": "0.0.0.0/0",
                     "protocol": protocol,
                     "port_range_min": str(group["guestport"]),
                     "port_range_max": str(group["guestport"])
                     }
                )

            yaml_dict["resources"][port]["properties"]["security_groups"].append({"get_resource": security_group})

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
        return self.get_meter_by_description("Number of virtual CPUs")

    def get_image(self):
        try:
            return get_text(self.data.getElementsByTagName("sasd:HostResource")[0].childNodes)
        except:
            return get_text(self.data.getElementsByTagName("rasd:HostResource")[0].childNodes)

    def get_network(self):
        network_dict = {"internal_network": [], "NAT": []}
        for network in self.data.getElementsByTagName("Adapter"):
            if network.getAttribute("enabled") == "true":
                element = network.getElementsByTagName("DisabledModes")[0]
                network.removeChild(element)
                if network.getElementsByTagName("InternalNetwork"):
                    network_dict["internal_network"].append(network.getElementsByTagName("InternalNetwork")[0].getAttribute("name"))
                if network.getElementsByTagName("NAT"):
                    network_dict["NAT"].append({"protocol": network.getElementsByTagName("Forwarding")[0].getAttribute("proto"),
                                                "guestport": network.getElementsByTagName("Forwarding")[0].getAttribute("guestport")})
        return network_dict
