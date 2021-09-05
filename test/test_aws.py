import json
import os

from api.resources.libs.aws_email import awsContactEmail


def get_data():
    with open('test/data.json') as f:
        data = json.load(f)
    return data


DATA = get_data()
RECIPIENT = os.environ.get('TEST_EMAIL_RECIPIENT')
EMAIL = awsContactEmail(DATA['message_info'], RECIPIENT)


def test_email_info():
    assert(EMAIL.sender == "Beantown Event <contact@beantownpub.com>")


def test_email_send():
    response = EMAIL.send_message()
    assert(response is None)
