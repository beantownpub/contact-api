import os

from flask import Response, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource
from api.libs.utils import add_creation_date, verify_password
from api.libs.logging import init_logger
from api.libs.slack import slack_message

AUTH = HTTPBasicAuth()
LOG = init_logger(os.environ.get("LOG_LEVEL").strip())
os.environ.get("SLACK_WEBHOOK_URL")


class SlackAPIException(Exception):
    """Base  class for order confirmation exceptions"""


class SlackAPI(Resource):
    @AUTH.login_required
    def post(self):
        body = request.get_json()
        LOG.info("SlackAPI | Body: %s", body)
        channel = body["channel"]
        message = add_creation_date(body["message"])
        response = slack_message(channel, message, URL)
        if response == 200:
            resp = {"status": 200, "response": "ok", "mimetype": "application/json"}
        else:
            SlackAPIException("Error sending message to slack | Status: %s", response)
        return Response(**resp)
