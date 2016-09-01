import os
import json
from flask import Blueprint, request
from werkzeug.utils import secure_filename


mod = Blueprint('file_uploading', __name__)

from app import app


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in app.config['ALLOWED_FILES']


@mod.route('/api/file/upload', methods=['POST'])
def simple_upload_receipt():
    ''' Receipt upload handler without DB connection and authentication.'''
    print request
    image_file = request.files['file']
    if image_file and allowed_file(image_file.filename):
        filename = secure_filename(image_file.filename)
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.mkdir(app.config['UPLOAD_FOLDER'])

        imagepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(imagepath)
        app.logger.debug("Upload OK, saved file " + imagepath)

        # TODO create a new receipt object to db and return it
    return json.dumps('Ok')
