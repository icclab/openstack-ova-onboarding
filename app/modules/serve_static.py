from flask import Blueprint

mod = Blueprint('serve_static', __name__)

from app import app


@mod.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/<path:path>')
def static_proxy(path):
    return app.send_static_file(path)
