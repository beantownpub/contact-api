import logging
import os
from flask import Flask, request
from flask_restful import Api
from flask_cors import CORS

from api.libs.logging import init_logger
from api.resources.routes import init_routes


class ContactAPIException(Exception):
    """Base class for merch API exceptions"""


ORIGINS = [
    "http://localhost:3000",
    "http://localhost",
    "https://beantownpub.com",
    "https://dev.beantownpub.com",
    "https://www.beantownpub.com"
]

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
APP = Flask(__name__.split(".")[0], instance_path="/opt/app/api")
API = Api(APP)

APP.config["CORS_ALLOW_HEADERS"] = True
APP.config["CORS_EXPOSE_HEADERS"] = True


cors = CORS(
    APP, resources={r"/v1/contact/*": {"origins": ORIGINS}}, supports_credentials=True
)

LOG = init_logger(LOG_LEVEL)
LOG.info("Logging initialized | Level %s", LOG_LEVEL)
init_routes(API)
LOG.info("Routes initialized")


@APP.after_request
def after_request(response):
    origin = request.environ.get("HTTP_ORIGIN")
    if origin and origin in ORIGINS:
        response.headers.add("Access-Control-Allow-Origin", origin)
    response.headers.add(
        "Access-Control-Allow-Headers", "Content-Type,Authorization,X-JAL-Comp"
    )
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response
