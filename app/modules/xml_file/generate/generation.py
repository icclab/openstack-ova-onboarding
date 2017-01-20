from app import app
import random
from xml.dom import minidom


def randomMAC():
    mac = [0x00, 0x16, 0x3e,
           random.randint(0x00, 0x7f),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    return ''.join(map(lambda x: "%02x" % x, mac))


class OVAFile:

    def __init__(self, ovf_version):
        self.ovf_version = ovf_version
        self.doc = minidom.Document()
        self.iterator = iter(app.config['PORT_RANGE'])

    def create_block_from_dict(self, block_name, map_dict):
        block = self.doc.createElement(block_name)
        for item in map_dict:
            raw = self.doc.createElement(item)
            block.appendChild(raw)
            raw_text = self.doc.createTextNode(map_dict[item])
            raw.appendChild(raw_text)
        return block

    def create_adapter(self, slot_number):
        adapter = self.doc.createElement('Adapter')
        adapter.setAttribute('slot', str(slot_number))
        adapter.setAttribute('enabled', 'true')
        adapter.setAttribute('MACAddress', randomMAC())
        adapter.setAttribute('cable', 'true')
        adapter.setAttribute('speed', '0')
        adapter.setAttribute('type', '82540EM')
        return adapter

    def base_setUP(self):
        envelop = self.doc.createElement('Envelope')
        self.doc.appendChild(envelop)
        envelop.setAttribute('ovf:version', self.ovf_version)
        envelop.setAttribute('xml:lang', 'en-US')
        envelop.setAttribute('xmlns', 'http://schemas.dmtf.org/ovf/envelope/2')
        envelop.setAttribute('xmlns:ovf', 'http://schemas.dmtf.org/ovf/envelope/2')
        envelop.setAttribute('xmlns:rasd',
                             'http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData')
        envelop.setAttribute('xmlns:vssd',
                             'http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_VirtualSystemSettingData')
        envelop.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        envelop.setAttribute('xmlns:vbox', 'http://www.virtualbox.org/ovf/machine')
        envelop.setAttribute('xmlns:epasd',
                             'http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_EthernetPortAllocationSettingData.xsd')
        envelop.setAttribute('xmlns:sasd',
                             'http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_StorageAllocationSettingData.xsd')

        reference = self.doc.createElement('References')
        envelop.appendChild(reference)

        disk_section = self.doc.createElement('DiskSection')
        envelop.appendChild(disk_section)
        disk_info = self.doc.createElement('Info')
        disk_section.appendChild(disk_info)
        disk_info_text = self.doc.createTextNode("List of the virtual disks used in the package")
        disk_info.appendChild(disk_info_text)

        network_section = self.doc.createElement('NetworkSection')
        envelop.appendChild(network_section)
        network_section_info = self.doc.createElement('Info')
        network_section.appendChild(network_section_info)
        network_section_info_text = self.doc.createTextNode("Logical networks used in the package")
        network_section_info.appendChild(network_section_info_text)

        virtual_system_collection = self.doc.createElement('VirtualSystemCollection')
        envelop.appendChild(virtual_system_collection)
        virtual_system_collection.setAttribute('ovf:name', 'ExportedVirtualBoxMachines')

    def add_machine(self, image_path, file_reference, disk_capacity, diskId, box_id,
                    machine_name, os_type, cpu_number, memory_size, version, uuid, list_of_ports, rules):
        file_name = self.doc.createElement('File')
        reference = self.doc.getElementsByTagName("References").item(0)
        reference.appendChild(file_name)
        file_name.setAttribute('ovf:href', image_path)
        file_name.setAttribute('ovf:id', file_reference)

        disk_section = self.doc.getElementsByTagName("DiskSection").item(0)
        disk = self.doc.createElement('Disk')
        disk_section.appendChild(disk)
        disk.setAttribute('ovf:capacity', disk_capacity)
        disk.setAttribute('ovf:diskId', diskId)
        disk.setAttribute('ovf:fileRef', file_reference)
        disk.setAttribute('ovf:format', 'http://www.vmware.com/interfaces/specifications/vmdk.html#streamOptimized')
        disk.setAttribute('vbox:uuid', box_id)
        virtual_system_collection = self.doc.getElementsByTagName("VirtualSystemCollection").item(0)
        virtual_system = self.doc.createElement('VirtualSystem')
        virtual_system_collection.appendChild(virtual_system)
        virtual_system.setAttribute('ovf:id', machine_name)
        virtual_system_info = self.doc.createElement('Info')
        virtual_system.appendChild(virtual_system_info)
        virtual_system_info_text = self.doc.createTextNode('A virtual machine')
        virtual_system_info.appendChild(virtual_system_info_text)
        operating_system_section = self.doc.createElement('OperatingSystemSection')
        virtual_system.appendChild(operating_system_section)
        operating_system_section.setAttribute('ovf:id', '80')
        operating_system_section_info = self.doc.createElement('Info')
        operating_system_section.appendChild(operating_system_section_info)
        operating_system_section_info_text = self.doc.createTextNode('The kind of installed guest operating system')
        operating_system_section_info.appendChild(operating_system_section_info_text)
        operating_system_section_description = self.doc.createElement('Description')
        operating_system_section.appendChild(operating_system_section_description)
        operating_system_section_description_text = self.doc.createTextNode(os_type)
        operating_system_section_description.appendChild(operating_system_section_description_text)
        vbox_ostype = self.doc.createElement('vbox:OSType')
        operating_system_section.appendChild(vbox_ostype)
        vbox_ostype.setAttribute('ovf:required', 'false')
        vbox_ostype_text = self.doc.createTextNode(os_type)
        vbox_ostype.appendChild(vbox_ostype_text)

        virtual_hardware_selection = self.doc.createElement('VirtualHardwareSection')
        virtual_system.appendChild(virtual_hardware_selection)
        virtual_hardware_selection_info = self.doc.createElement('Info')
        virtual_hardware_selection.appendChild(virtual_hardware_selection_info)
        virtual_hardware_selection_info_text = self.doc.createTextNode('Virtual hardware requirements for a virtual machine')
        virtual_hardware_selection_info.appendChild(virtual_hardware_selection_info_text)

        virtual_hardware_selection.appendChild(
            self.create_block_from_dict('System',
                                   {'vssd:ElementName': 'Virtual Hardware Family',
                                    'vssd:InstanceID': '0',
                                    'vssd:VirtualSystemIdentifier': machine_name,
                                    'vssd:VirtualSystemType': 'virtualbox-2.2'}
                                   )
        )

        virtual_hardware_selection.appendChild(
            self.create_block_from_dict('Item',
                                   {'rasd:Caption': cpu_number + ' virtual CPU',
                                    'rasd:Description': 'Number of virtual CPUs',
                                    'rasd:InstanceID': '1',
                                    'rasd:ResourceType': '3',
                                    'rasd:VirtualQuantity': cpu_number}
                                   )
        )

        virtual_hardware_selection.appendChild(
            self.create_block_from_dict('Item',
                                   {'rasd:AllocationUnits': 'MegaBytes',
                                    'rasd:Caption': memory_size + ' MB of memory',
                                    'rasd:Description': 'Memory Size',
                                    'rasd:InstanceID': '2',
                                    'rasd:ResourceType': '4',
                                    'rasd:VirtualQuantity': memory_size}
                                   )
        )

        virtual_hardware_selection.appendChild(
            self.create_block_from_dict('Item',
                                   {'rasd:Address': '0',
                                    'rasd:Caption': 'sataController0',
                                    'rasd:Description': 'SATA Controller',
                                    'rasd:InstanceID': '3',
                                    'rasd:ResourceSubType': 'AHCI',
                                    'rasd:ResourceType': '20'
                                    }
                                   )
        )

        virtual_hardware_selection.appendChild(
            self.create_block_from_dict('StorageItem',
                                   {'sasd:AddressOnParen': '0',
                                    'sasd:Caption': diskId,
                                    'sasd:Description': 'Disk Image',
                                    'sasd:HostResource': '/disk/' + diskId,
                                    'sasd:InstanceID': '4',
                                    'sasd:Parent': '3',
                                    'sasd:ResourceType': '17'
                                    }
                                   )
        )

        vbox_machine = self.doc.createElement('vbox:Machine')
        virtual_system.appendChild(vbox_machine)
        vbox_machine.setAttribute('ovf:required', 'false')
        vbox_machine.setAttribute('version', version)
        vbox_machine.setAttribute('uuid', uuid)
        vbox_machine.setAttribute('name', machine_name)
        vbox_machine.setAttribute('OSType', os_type)
        ovf_info = self.doc.createElement('ovf:Info')
        vbox_machine.appendChild(ovf_info)
        ovf_info_text = self.doc.createTextNode('Complete VirtualBox machine configuration in VirtualBox format')
        ovf_info.appendChild(ovf_info_text)
        hardware = self.doc.createElement('Hardware')
        vbox_machine.appendChild(hardware)
        hardware.setAttribute('version', '2')

        cpu = self.doc.createElement('CPU')
        hardware.appendChild(cpu)
        cpu.setAttribute('count', cpu_number)

        memory = self.doc.createElement('Memory')
        hardware.appendChild(memory)
        memory.setAttribute('RAMSize', memory_size)

        network = self.doc.createElement('Network')
        hardware.appendChild(network)
        slot_number = 0
        if rules:
            adapter = self.create_adapter(slot_number)
            network.appendChild(adapter)
            nat = self.doc.createElement('NAT')
            adapter.appendChild(nat)
            for rule in sorted(rules, key=lambda k: k['port']):
                forwarding = self.doc.createElement('Forwarding')
                if rule['ip_protocol'] == 'tcp':
                    forwarding.setAttribute('proto', '1')
                else:
                    forwarding.setAttribute('proto', '0')
                hostport = str(next(self.iterator))
                forwarding.setAttribute('name', rule['ip_protocol']+hostport)
                forwarding.setAttribute('guestport', str(rule['port']))
                forwarding.setAttribute('hostport', hostport)
                nat.appendChild(forwarding)

            slot_number += 1

        for port in list_of_ports:
            if not (port == app.config['PUBLIC_NET']):
                adapter = self.create_adapter(slot_number)
                network.appendChild(adapter)
                int_network = self.doc.createElement('InternalNetwork')
                int_network.setAttribute('name', port)
                adapter.appendChild(int_network)
                slot_number += 1

        storage_controllers = self.doc.createElement('StorageControllers')
        vbox_machine.appendChild(storage_controllers)

        storage_controller = self.doc.createElement('StorageController')
        storage_controllers.appendChild(storage_controller)
        storage_controller.setAttribute('name', 'SATA')
        storage_controller.setAttribute('type', 'AHCI')
        storage_controller.setAttribute('PortCount', '1')
        attached_device = self.doc.createElement('AttachedDevice')
        storage_controller.appendChild(attached_device)
        attached_device.setAttribute('type', 'HardDisk')
        attached_device.setAttribute('port', '0')
        attached_device.setAttribute('device', '0')
        image = self.doc.createElement('Image')
        attached_device.appendChild(image)
        image.setAttribute('uuid', '{' + box_id + '}')

    def get_xml_file(self, path):
        xml_str = self.doc.toprettyxml(indent=" ")

        with open(path, "w") as f:
            f.write(xml_str)