import uuid
import tarfile
import subprocess
from app.modules.openstack.glance import GlanceClient
from app.modules.openstack.nova import NovaClient
from app.modules.xml_file.generate.generation import OVAFile
from flask import Blueprint, request
from openstack.session import get_valid_session
from backend_logging import LOG
import time
import sys
import os


mod = Blueprint('generating', __name__)

from app import app

temp_location = app.config['UPLOAD_FOLDER']


def make_tarfile(source_dir, order):
    with tarfile.open(source_dir + ".ova", "w") as tar:
        for point in order:
            ovf_path = source_dir + "/" + point
            tar.add(ovf_path, arcname=os.path.basename(ovf_path))
            os.remove(ovf_path)


@mod.route('/api/generate', methods=['POST'])
def generate():
    openstack = request.form
    region = openstack['region']
    session = get_valid_session(openstack)
    nova = NovaClient(session=session.session, version=2, region=region)
    glance = GlanceClient(session=session.session, version=2, region=region)
    if nova.get_status() and glance.get_status():
        LOG.info("Connection to all services are established")
        ovf_version = "2.0"
        my_file = OVAFile(ovf_version)
        my_file.base_setUP()
        output_folder = str(uuid.uuid4())
        os.mkdir(temp_location + output_folder)
        ova_path = temp_location + output_folder

        def wait_until_image(image_id, period=0.25):
            while glance.get_image(image_id)["status"] != "active":
                time.sleep(period)
            return True

        def save_image(image_id, path):
            """Save an image to the specified path.
            :param image_id: image id
            :param path: path to save the image to
            """
            wait_until_image(image_id)
            LOG.info("Image is saved as snapshot")
            data = glance.get_image_data(image_id)
            if path is None:
                image = getattr(sys.stdout, 'buffer',
                                sys.stdout)
            else:
                image = open(path, 'wb')
            try:
                for chunk in data:
                    image.write(chunk)
            finally:
                if path is not None:
                    image.close()

        number = 1
        order_list = ['ova']
        for instance_id in (dict(openstack))['instance_id']:
            nova_instance = nova.get_instance_by_id(instance_id)
            unique_ind = str(uuid.uuid4())
            name = nova_instance.name + unique_ind
            flavor = nova.get_flavor(id=nova_instance.flavor['id'])
            file_reference = "file" + str(number)
            image_name = name + '.vmdk'
            machine_name = nova_instance.name
            disk_capacity = str(flavor.disk*1024*1024*1024)
            diskId = "vmdisk" + str(number)
            box_id = str(uuid.uuid4())
            box_uuid = "{2f07cea2-4c31-44fa-8e96-31aada3ccaa3}"
            os_type = "RedHat_64"
            version = "1.12-linux"
            cpu_number = str(flavor.vcpus)
            memory_size = str(flavor.ram)
            qcow_path = temp_location + name + '.qcow2'
            rules = nova.get_security_rules(nova_instance)
            if len(app.config['PORT_RANGE']) < len(rules):
                raise Exception("Not enough ports available for security groups are available")
            my_file.add_machine(image_name, file_reference, disk_capacity, diskId, box_id,
                                machine_name, os_type, cpu_number, memory_size, version,
                                box_uuid, nova_instance.networks, rules)
            image_id = nova.create_image_from_instance(instance_id, nova_instance.name)
            save_image(image_id, qcow_path)
            glance.remove_image(image_id)
            subprocess.call(['qemu-img', 'convert', '-f', 'qcow2', '-O', 'vmdk', '-o', 'subformat=streamOptimized',
                             qcow_path, ova_path + "/" + name + '.vmdk'])
            os.remove(qcow_path)
            LOG.info("Image is downloaded as " + name + ".qcow2")
            order_list.append(name + ".vmdk")
            number += 1
        my_file.get_xml_file(ova_path + "/" + output_folder + '.ovf')
        order_list[0] = output_folder + '.ovf'
        make_tarfile(ova_path, order_list)
        LOG.info("File is saved as " + output_folder + " file")
        os.rmdir(ova_path)

    return str({"Ok"})
