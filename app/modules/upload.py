import os
import shutil
import yaml
import uuid
from backend_logging import LOG
from werkzeug.utils import secure_filename
from app.modules.xml_file.parsed.file import extract_file, transform_parsed_vms
from app.modules.xml_file.parsed.vm import generate_template
from flask import Blueprint, request
from xml_file.reader import GeneratedVM
from openstack.session import get_valid_session
from openstack.glance import GlanceClient
from openstack.nova import NovaClient, from_bytes_to_gb
from openstack.heat import HeatClient

mod = Blueprint('uploading', __name__)

from app import app

temp_location = app.config['UPLOAD_FOLDER']


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in app.config['ALLOWED_FILES']


def add_uuid(filename):
    return filename.rsplit('.', 1)[0] + str(uuid.uuid1()) + "." + filename.rsplit('.', 1)[1]


def clean(folder):
    os.remove(folder + ".ova")
    os.remove(folder + ".tar")
    shutil.rmtree(folder)


@mod.route('/api/upload', methods=['POST'])
def upload():
    openstack = request.form
    region = openstack['region']
    session = get_valid_session(openstack)
    nova = NovaClient(session=session.session, version=2, region=region)
    glance = GlanceClient(session=session.session, version=2, region=region)
    heat = HeatClient(version=1, endpoint=session.get_endpoint("heat", region), token=session.token)
    image_list = []
    if nova.get_status() and glance.get_status() and heat.get_status():
        LOG.info("Connection to all services are established")
        image_file = request.files['file']
        if image_file and allowed_file(image_file.filename):
            filename = add_uuid(secure_filename(image_file.filename))
            if not os.path.exists(temp_location):
                os.mkdir(temp_location)
            imagepath = os.path.join(temp_location, filename)
            LOG.info("Saving file to: " + imagepath + " ...")
            image_file.save(imagepath)
            LOG.info("Upload OK, saved file " + imagepath)
        else:
            raise Exception("Extension is not allowed")
        LOG.info("Extracting ova file to " + temp_location + "file ...")
        ovf_file = extract_file(filename, temp_location)
        folder = temp_location+ovf_file.replace(".ovf", "")
        try:
            LOG.info("Parsing virtual information data from ovf file ...")
            parsed_file = transform_parsed_vms(folder + '/'+image_file.filename.replace("ova", "ovf"))
            valid_vms = []
            space_available, message = nova.check_quota(parsed_file["vms"])
            if space_available:
                LOG.info(message)
                for vm in parsed_file["vms"]:
                    flavor = nova.get_best_flavor([int(vm.cpu), int(vm.ram), from_bytes_to_gb(vm.disk)])
                    image_id = glance.upload_image(vm.image, folder + '/' + vm.image)
                    point = GeneratedVM(name=vm.name,
                                        flavor=flavor,
                                        image=image_id,
                                        networks=vm.network["internal_network"],
                                        sec_groups=vm.network["NAT"])
                    image_list.append(image_id)
                    valid_vms.append(point)
                LOG.info("Generating template file ...")
                heat.create_stack(name=openstack['stack_name'], body=yaml.dump(generate_template(valid_vms)))
            else:
                raise Exception(message)
        except:
            glance.remove_list_of_images(image_list)
            clean(folder)
            raise Exception("Couldn't create heat template")
        clean(folder)
        return str({"Ok"})
    else:
        LOG.error("Couldn't establish connection with all services")
