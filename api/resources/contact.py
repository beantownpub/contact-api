import json
import logging
import os

import requests
from flask import Response, request
from flask_restful import Resource
from .libs.aws_email import awsContactEmail


app_log = logging.getLogger()

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app_log.handlers = gunicorn_logger.handlers
    app_log.setLevel('INFO')


def aws_send_email(body):
    message_info = {
        "name": body.get('name', 'Not Provided'),
        "phone_number": body.get('phone', 'Not Provided'),
        "email": body.get('email', 'Not Provided'),
        "event_date": body.get('event_date', 'Not Provided'),
        "details": body.get('details', 'Not Provided'),
        "location": body.get('location')
    }
    app_log.info('- aws_send_email | Message info: %s', message_info)
    recipient = os.environ.get('EMAIL_RECIPIENT')
    email = awsContactEmail(message_info, recipient)
    response = email.send_message()
    return response


def slack_message(body):
    app_log.info('- slack_message: %s', body)
    url = os.environ.get('SLACK_WEBHOOK_URL')
    channel = os.environ.get('SLACK_WEBHOOK_CHANNEL')
    user = os.environ.get('SLACK_WEBHOOK_USER')
    headers = {'Content-type': 'application/json'}
    webhook = {
        "channel": channel,
        "username": user,
        "text": f"```{json.dumps(body, indent=2)}```"
    }
    response = []
    retries, max_retries = 0, 2
    while not response and retries < max_retries:
        try:
            req = requests.post(url, headers=headers, data=str(webhook))
            response = req.status_code
        except requests.exceptions.ConnectionError as err:
            app_log.error(f"Slack Connection Error\n\n{err}\n\n")
            retries += 1
            if retries >= max_retries:
                return None
            req = requests.post(url, headers=headers, data=str(webhook))
            response = req.status_code
        else:
            break
    return response


class EventContactAPI(Resource):
    success = 'Request Received! We will respond to you as soon as we can. Thanks!'
    failure = [
        'Error Sending Request. Please try again.',
        'If error persists email request to beantownpubboston@gmail.com'
    ]

    def get(self, location):
        version = {"app": "contact_api", "version": "0.1.0", "location": location}
        app_log.info('- ContactAPI | Version: %s', version)
        return Response(json.dumps(version), mimetype='application/json', status=200)

    def post(self, location):
        body = request.get_json()
        body['location'] = location
        app_log.info('- ContactAPI | Location: %s', location)
        aws_send_email(body)
        if slack_message(body) == 200:
            data = {'msg': self.success}
        else:
            data = {'msg': ' '.join(self.failure)}
        return data, 200

    def options(self, location):
        app_log.info('- ContactAPI | OPTIONS | %s', location)
        return '', 200


class MerchContactAPI(Resource):
    success = 'Request Received! We will respond to you as soon as we can. Thanks!'
    failure = [
        'Error Sending Request. Please try again.',
        'If error persists email request to beantownpubboston@gmail.com'
    ]

    def get(self):
        order = request.get_json()
        version = {"app": "merch_contact_api", "version": "0.1.0", "order": order}
        return Response(version, mimetype='application/json', status=200)

    def post(self):
        body = request.get_json()
        app_log.info('- MerchContactAPI | Body: %s', body)
        # send_email(body)
        if slack_message(body) == 200:
            data = {'msg': self.success}
        else:
            data = {'msg': ' '.join(self.failure)}
        return data, 200

    def options(self):
        order = request.get_json()
        app_log.info('- ContactAPI | OPTIONS | %s', order)
        return '', 200
