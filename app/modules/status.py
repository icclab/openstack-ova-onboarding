import json
from backend_logging import LOG
from flask import Blueprint, request
from openstack.session import Session
from openstack.nova import NovaClient
from openstack.glance import GlanceClient
from openstack.heat import HeatClient

mod = Blueprint('status', __name__)


@mod.route('/api/status', methods=['POST'])
def status():
    openstack = request.json
    region = openstack['region']
    if request.method == 'POST':
        session = Session(auth_url=openstack['url'],
                          username=openstack['username'],
                          password=openstack['password'],
                          tenant_name=openstack['tenant_name'])
        LOG.info("Getting nova client connection")
        nova = NovaClient(session=session.session, version=2, region=region)
        LOG.info("Getting glance client connection")
        glance = GlanceClient(session=session.session, version=2, region=region)
        LOG.info("Getting heat client connection")
        heat = HeatClient(version=1, endpoint=session.get_endpoint("heat", region), token=session.token)
        response = {"nova_status": nova.get_status(),
                    "glance_status": glance.get_status(),
                    "heat_status": heat.get_status()}
        return json.dumps(response)
