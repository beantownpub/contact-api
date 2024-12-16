import os
from datetime import datetime
from flask_httpauth import HTTPBasicAuth
from api.libs.logging import init_logger

LOG = init_logger(os.environ.get("LOG_LEVEL").strip())
AUTH = HTTPBasicAuth()


def add_creation_date(message_body):
    created = datetime.strftime(datetime.today(), "%m-%d-%Y %H:%M")
    message_body["created"] = created
    return message_body


@AUTH.verify_password
def verify_password(username, password):
    LOG.info("Verifying credentials for user %s", username)
    api_username = os.environ.get("API_USERNAME").strip()
    api_password = os.environ.get("API_PASSWORD").strip()
    if username.strip() == api_username and password.strip() == api_password:
        verified = True
    else:
        verified = False
    return verified
