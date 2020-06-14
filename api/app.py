import logging
import os
from flask import Flask
from flask_restful import Api
from flask_cors import CORS

from api.resources.routes import init_routes


class ContactAPIException(Exception):
    """Base class for merch API exceptions"""


LOG_LEVEL = os.environ.get('CONTACT_API_LOG_LEVEL', 'INFO')
ORIGIN_URL = os.environ.get('ORIGIN_URL', 'https://beantown.jalgraves.com')
APP = Flask(__name__.split('.')[0], instance_path='/opt/app/api')
API = Api(APP)

APP.config['CORS_ALLOW_HEADERS'] = True
APP.config['CORS_EXPOSE_HEADERS'] = True


cors = CORS(
    APP,
    resources={r"/v1/*": {"origins": ["http://localhost:3000", "http://localhost"]}},
    supports_credentials=True
)

init_routes(API)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    APP.logger.handlers = gunicorn_logger.handlers
    APP.logger.setLevel(LOG_LEVEL)


@APP.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', "http://localhost:3000")
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-JAL-Comp')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response
