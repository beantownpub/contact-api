import json
import os

from api.libs.notify import EventRequest, OrderConfirmation


def get_data():
    with open("test/data.json") as f:
        data = json.load(f)
    return data


DATA = get_data()
RECIPIENT = os.environ.get("TEST_EMAIL_RECIPIENT")
EVENT_REQUEST = EventRequest(DATA["message_info"], RECIPIENT)
CONFIRMATION_EMAIL = OrderConfirmation(
    {"order": DATA["order_info"], "payment": DATA["payment"]}, recipient=RECIPIENT
)


def test_email_info():
    assert EVENT_REQUEST.sender == "Beantown Event <contact@beantownpub.com>"
    assert RECIPIENT.find("@gmail") != -1
    assert EVENT_REQUEST._format_phone_number() == "555-666-1234"
    assert CONFIRMATION_EMAIL.recipient.find("@") != -1


def test_email_send():
    response = EVENT_REQUEST.send_email()
    assert response is None
    slack_response = EVENT_REQUEST.send_slack()
    assert slack_response == 200


def test_confirmation_email_send():
    response = CONFIRMATION_EMAIL.send_email()
    assert response is None
    slack_response = CONFIRMATION_EMAIL.send_slack()
    assert slack_response == 200
