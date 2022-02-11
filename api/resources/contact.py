import json
import os

from flask import Response, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource
from api.libs.notify import EventRequest, OrderConfirmation
from api.libs.logging import init_logger

AUTH = HTTPBasicAuth()
LOG = init_logger(os.environ.get('LOG_LEVEL'))



class OrderConfirmationException(Exception):
    """Base  class for order confirmation exceptions"""


@AUTH.verify_password
def verify_password(username, password):
    LOG.info("Verifying user %s", username)
    if password == os.environ.get("API_PASSWORD"):
        return True
    return False


class EventContactAPI(Resource):
    success = 'Request Received! We will respond to you as soon as we can. Thanks!'
    failure = [
        'Error Sending Request. Please try again.',
        'If error persists email request to beantownpubboston@gmail.com'
    ]

    @AUTH.login_required
    def get(self, location):
        version = {"app": "contact_api", "version": "0.1.7", "location": location}
        LOG.info('- ContactAPI | Version: %s', version)
        return Response(json.dumps(version), mimetype='application/json', status=200)

    @AUTH.login_required
    def post(self, location):
        body = request.get_json()
        body['location'] = location
        LOG.info('Body: %s', body)
        message = EventRequest(body)
        slack_status = message.send_slack()
        message.send_email()
        if slack_status == 200:
            resp = {"status": 200, "response": self.success, "mimetype": "application/json"}
        else:
            LOG.error('Slack send exception | %s', slack_status)
            resp = {"status": 200, "response": " ".join(self.failure), "mimetype": "application/json"}
        return Response(**resp)

    def options(self, location):
        LOG.info('ContactAPI | OPTIONS | %s', location)
        return '', 200


class MerchContactAPI(Resource):
    success = 'Request Received! We will respond to you as soon as we can. Thanks!'
    failure = [
        'Error Sending Request. Please try again.',
        'If error persists email request to beantownpubboston@gmail.com'
    ]

    @AUTH.login_required
    def get(self):
        order = request.get_json()
        version = {"app": "merch_contact_api", "version": "0.1.0", "order": order}
        return Response(version, mimetype='application/json', status=200)

    @AUTH.login_required
    def post(self):
        body = request.get_json()
        LOG.info('MerchContactAPI | Body: %s', body)
        message = OrderConfirmation(body)
        slack_status = message.send_slack()
        if slack_status != 200:
            LOG.error('Slack send exception | %s', body)
        message.send_email()
        resp = {"status": 200, "response": "wtf", "mimetype": "application/json"}
        return Response(**resp)

    def options(self):
        order = request.get_json()
        LOG.info('- ContactAPI | OPTIONS | %s', order)
        return '', 200
