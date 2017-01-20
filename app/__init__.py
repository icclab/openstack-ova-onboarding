from flask import Flask

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = '/home/lexxito/temp/'
app.config['ALLOWED_FILES'] = ['ova']
app.config['CIDR'] = '172.168.0.0/24'
app.config['PUBLIC_NET'] = 'private'
#app.config['PUBLIC_NET'] = 'c57d2c93-e6c6-455c-bc05-6f1663d58a2a'
app.config['HEAT_VERSION'] = '2014-10-16'
app.config['PORT_RANGE'] = range(2200, 3000)

from modules import serve_static
app.register_blueprint(serve_static.mod, url_prefix='/')

from modules import status
app.register_blueprint(status.mod)

from modules import upload
app.register_blueprint(upload.mod)

from modules import generate
app.register_blueprint(generate.mod)



