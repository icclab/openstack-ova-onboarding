import json
from backend_logging import LOG
from flask import Blueprint, request
from openstack.session import get_valid_session
from openstack.nova import NovaClient
from openstack.glance import GlanceClient
from openstack.heat import HeatClient

mod = Blueprint('status', __name__)


@mod.route('/api/status', methods=['POST'])
def status():
    openstack = request.form
    region = openstack['region']
    if request.method == 'POST':
        credentials_status = False
        import_status = False
        export_status = False
        session = get_valid_session(openstack)
        LOG.info("Getting nova client connection")
        nova = NovaClient(session=session.session, version=2, region=region)
        LOG.info("Getting glance client connection")
        glance = GlanceClient(session=session.session, version=2, region=region)
        LOG.info("Getting heat client connection")
        heat = HeatClient(version=1, endpoint=session.get_endpoint("heat", region), token=session.token)
        if nova.get_status() and glance.get_status() and heat.get_status():
            credentials_status = True
        if credentials_status and openstack['method'] == 'import':
            import_status = True
        if credentials_status and openstack['method'] == 'export':
            export_status = True
        response = {"credentials_status": credentials_status,
                    "import_status": import_status,
                    "export_status": export_status}
        return json.dumps(response)