import json
import logging
import os
import smtplib

import requests
from flask import Response, request
from flask_restful import Resource

app_log = logging.getLogger()

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app_log.handlers = gunicorn_logger.handlers
    app_log.setLevel('INFO')


def send_email(body):
    app_log.info('- send_email | Body: %s', body)
    name = body.get('name', 'Not Provided')
    phone = body.get('phone', 'Not Provided')
    email = body.get('email', 'Not Provided')
    event_date = body.get('event_date', 'Not Provided')
    details = body.get('details', 'Not Provided')
    location = body.get('location', 'Not Provided')
    sender = os.environ.get('EMAIL_SENDER')
    recipient = os.environ.get('EMAIL_RECIPIENT')
    body = [
        f'From: {sender}',
        f'To: {recipient}',
        f'Subject: Private Event Request for {location}\n',
        f'Hello,\n\nYou have a new private event information request from {location}\n',
        f'Event Info:\n',
        f'Name: {name}',
        f'Phone: {phone}',
        f'Email: {email}',
        f'Date: {event_date}',
        f'Details: {details}'
    ]
    password = os.environ.get('CONTACT_GMAIL_PASSWORD')
    message = "\n".join(body).encode()
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(sender, password)
    server.sendmail(sender, recipient, message)
    server.close()


def slack_message(body):
    app_log.info('- slack_message | Body: %s', body)
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


class ContactAPI(Resource):
    success = 'Request Received! We will respond to you as soon as we can. Thanks!'
    failure = [
        'Error Sending Request. Please try again.',
        'If error persists email request to beantownpubboston@gmail.com'
    ]
    def get(self, location):
        version = {"app": "contact_api", "version": "0.1.0", "location": location}
        return Response(version, mimetype='application/json', status=200)

    def post(self, location):
        body = request.get_json()
        body['location'] = location
        app_log.info('- ContactAPI | Body: %s', body)
        # send_email(body)
        if slack_message(body) == 200:
            data = {'msg': self.success}
        else:
            data = {'msg': ' '.join(self.failure)}
        return data, 200

    def options(self, location):
        app_log.info('- ContactAPI | OPTIONS | %s', location)
        return Response(status=200)
