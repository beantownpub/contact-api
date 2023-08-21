import json
import os

from flask import Response, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource
from api.libs.notify import EventRequest, OrderConfirmation
from api.libs.logging import init_logger

AUTH = HTTPBasicAuth()
LOG = init_logger(os.environ.get("LOG_LEVEL"))


class OrderConfirmationException(Exception):
    """Base  class for order confirmation exceptions"""


@AUTH.verify_password
def verify_password(username, password):
    api_username = os.environ.get("API_USERNAME").strip()
    api_password = os.environ.get("API_PASSWORD").strip()
    if username.strip() == api_username and password.strip() == api_password:
        verified = True
    else:
        verified = False
    return verified


class EventContactAPI(Resource):
    success = "Request Received! We will respond to you as soon as we can. Thanks!"
    failure = [
        "Error Sending Request. Please try again.",
        "If error persists email request to beantownpubboston@gmail.com",
    ]
    recipient = os.environ.get("EMAIL_RECIPIENT")
    test_recipient = os.environ.get("TEST_EMAIL_RECIPIENT")

    @AUTH.login_required
    def get(self, location):
        version = {"app": "contact_api", "version": "0.1.11", "location": location}
        LOG.info("- ContactAPI | Version: %s", version)
        return Response(json.dumps(version), mimetype="application/json", status=200)

    @AUTH.login_required
    def post(self, location):
        body = request.get_json()
        body["location"] = location
        LOG.info("Body: %s", body)
        if body["name"] == "Jonny Graves Test":
            email_recipient = self.test_recipient
            LOG.info("Sending email to test account %s", self.test_recipient)
        else:
            email_recipient = self.recipient
        message = EventRequest(body, email_recipient)
        slack_status = message.send_slack()
        message.send_email()
        if slack_status == 200:
            resp = {
                "status": 200,
                "response": self.success,
                "mimetype": "application/json",
            }
        else:
            LOG.error("Slack send exception | %s", slack_status)
            resp = {
                "status": 400,
                "response": " ".join(self.failure),
                "mimetype": "application/json",
            }
        return Response(**resp)

    def options(self, location):
        LOG.info("ContactAPI | OPTIONS | %s", location)
        return "", 200


class MerchContactAPI(Resource):
    success = "Request Received! We will respond to you as soon as we can. Thanks!"
    failure = [
        "Error Sending Request. Please try again.",
        "If error persists email request to beantownpubboston@gmail.com",
    ]

    @AUTH.login_required
    def get(self):
        order = request.get_json()
        version = {"app": "merch_contact_api", "version": "0.1.0", "order": order}
        return Response(version, mimetype="application/json", status=200)

    @AUTH.login_required
    def post(self):
        body = request.get_json()
        LOG.info("MerchContactAPI | Body: %s", body)
        message = OrderConfirmation(body)
        slack_status = message.send_slack()
        if slack_status != 200:
            LOG.error("Slack send exception | %s", body)
        message.send_email()
        resp = {"status": 200, "response": "wtf", "mimetype": "application/json"}
        return Response(**resp)

    def options(self):
        order = request.get_json()
        LOG.info("- ContactAPI | OPTIONS | %s", order)
        return "", 200
