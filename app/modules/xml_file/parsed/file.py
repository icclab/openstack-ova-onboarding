import tarfile
from xml.dom import minidom
from shutil import copyfile

from app.modules.xml_file.parsed.vm import ParsedVM
from app.modules.xml_file.reader import VM
from os.path import splitext


def extract_file(ova_file, temp_location):
    # Get the name of file
    pre, ext = splitext(ova_file)
    # Copy and rename file
    temp_tar = temp_location+pre+".tar"
    copyfile(temp_location+ova_file, temp_tar)
    # Extract file
    ova = tarfile.open(temp_tar, 'r')
    ova.extractall(temp_location)
    return pre+".ovf"


def transform_parsed_vms(ovf_file):
    parsed_file = ParsedFile(ovf_file)
    list_vms = []
    list_results = {}
    for parsed_vm in parsed_file.get_vms():
        for image in parsed_file.get_map():
            if image in parsed_vm.get_image():
                list_vms.append(VM(name=parsed_vm.get_name(),
                                   cpu=parsed_vm.get_cpu(),
                                   ram=parsed_vm.get_memory(),
                                   image=parsed_file.get_map()[image],
                                   network=parsed_vm.get_network()
                                   )
                                )
    list_results["vms"] = list_vms
    return list_results


class ParsedFile:
    def __init__(self, file_name):
        self.ElementTree = minidom.parse(file_name)

    def get_vms(self):
        systems = self.ElementTree.getElementsByTagName("VirtualSystem")
        list_parsed_vms = []
        for System in systems:
            vm = ParsedVM(System)
            list_parsed_vms.append(vm)
        return list_parsed_vms

    def get_map(self):
        image_map = {}
        for element in self.ElementTree.getElementsByTagName("File"):
            image_map[element.getAttribute("ovf:id")] = element.getAttribute("ovf:href")
        for element in self.ElementTree.getElementsByTagName("Disk"):
            image_map[element.getAttribute("ovf:diskId")] = image_map.pop(element.getAttribute("ovf:fileRef"))
        return image_map