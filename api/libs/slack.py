import json
import os
import requests

from .logging import init_logger
from .aws import get_secret

SECRET = get_secret()

URL = SECRET["slack_webhook_url"]
# CHANNEL = os.environ.get('SLACK_WEBHOOK_CHANNEL')
USER = SECRET["slack_user"]
HEADERS = {"Content-type": "application/json"}
LOG_LEVEL = os.environ.get("LOG_LEVEL").strip()
LOG = init_logger(LOG_LEVEL)


class SlackSendException(Exception):
    """base class for slack message sending exceptions"""


def slack_message(channel, body, webhook_url):
    LOG.debug("| Slack notification | %s", body)
    webhook = {
        "username": USER,
        "channel": channel,
        "text": f"```{json.dumps(body, indent=2)}```",
    }
    response = []
    retries, max_retries = 0, 2
    while not response and retries < max_retries:
        try:
            req = requests.post(webhook_url, headers=HEADERS, data=json.dumps(webhook))
            response = req.status_code
            if response != 200:
                LOG.error("Slack failure %s | %s", response, req.content)
                raise SlackSendException("Unable to send Slack message:\n%s", webhook)
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
