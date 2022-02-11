import json
import os
import requests

from .logging import init_logger

URL = os.environ.get('SLACK_WEBHOOK_URL')
# CHANNEL = os.environ.get('SLACK_WEBHOOK_CHANNEL')
USER = os.environ.get('SLACK_WEBHOOK_USER')
HEADERS = {'Content-type': 'application/json'}
LOG_LEVEL = os.environ.get('LOG_LEVEL')
LOG = init_logger(LOG_LEVEL)


class SlackSendException(Exception):
    """base class for slack message sending exceptions"""


def slack_message(body, webhook_url):
    LOG.info('| Slack notification | %s', body)
    webhook = {
        "username": USER,
        "text": f"```{json.dumps(body, indent=2)}```"
    }
    response = []
    retries, max_retries = 0, 2
    while not response and retries < max_retries:
        try:
            req = requests.post(webhook_url, headers=HEADERS, data=json.dumps(webhook))
            response = req.status_code
            if response != 200:
                LOG.error('Slack failure %s | %s', response, req.content)
                raise SlackSendException('Unable to send Slack message:\n%s', webhook)
        except requests.exceptions.ConnectionError as err:
            LOG.error(f"Slack Connection Error\n\n{err}\n\n")
            retries += 1
            if retries >= max_retries:
                return None
            req = requests.post(webhook_url, headers=HEADERS, data=json.dumps(webhook))
            response = req.status_code
        else:
            break
    return response