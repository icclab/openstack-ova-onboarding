import yaml
from backend_logging import LOG
from app.modules.xml_file.parsed.file import extract_file, transform_parsed_vms
from app.modules.xml_file.parsed.vm import generate_template
from flask import Blueprint, request
from xml_file.reader import GeneratedVM
from openstack.session import Session
from openstack.glance import GlanceClient
from openstack.nova import NovaClient
from openstack.heat import HeatClient

mod = Blueprint('uploading', __name__)

from app import app

temp_location = app.config['UPLOAD_FOLDER']


@mod.route('/api/upload', methods=['POST'])
def upload():
    openstack = request.json
    region = openstack['region']
    session = Session(auth_url=openstack['url'],
                      username=openstack['username'],
                      password=openstack['password'],
                      tenant_name=openstack['tenant_name'])
    nova = NovaClient(session=session.session, version=2, region=region)
    glance = GlanceClient(session=session.session, version=2, region=region)
    heat = HeatClient(version=1, endpoint=session.get_endpoint("heat", region), token=session.token)
    if nova.get_status() and glance.get_status() and heat.get_status():
        LOG.info("Connection to all services are established")
        LOG.info("Extracting ova file to " + temp_location + "file ...")
        ovf_file = extract_file(openstack['ova_file'], temp_location)
        LOG.info("Parsing virtual information data from ovf file ...")
        parsed_file = transform_parsed_vms(temp_location+ovf_file)
        valid_vms = []
        for vm in parsed_file["vms"]:
            flavor = nova.get_best_flavor([int(vm.cpu), int(vm.ram), 0])
            image_id = glance.upload_image(vm.image, temp_location + vm.image)
            point = GeneratedVM(name=vm.name,
                                flavor=flavor,
                                image=image_id,
                                networks=vm.network["internal_network"],
                                sec_groups=vm.network["NAT"])
            valid_vms.append(point)
        LOG.info("Generating template file ...")
        heat.create_stack(name=openstack['stack_name'], body=yaml.dump(generate_template(valid_vms)))
        return str({"Ok"})
    else:
        LOG.error("Couldn't establish connection with all services")

