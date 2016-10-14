from flask import Flask

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = '/home/lexxito/temp/'
app.config['ALLOWED_FILES'] = ['ova']
app.config['CIDR'] = '172.168.0.0/24'
app.config['PUBLIC_NET'] = 'private'

from modules import serve_static
app.register_blueprint(serve_static.mod, url_prefix='/')

from modules import upload
app.register_blueprint(upload.mod)


