import os

from datetime import datetime

from api.libs.aws import send_message
from api.libs.logging import init_logger
from api.libs.templates import confirmation_email, event_request_html, event_request_raw
from api.libs.slack import slack_message
from api.libs.utils import add_creation_date

DEFAULT_WEBHOOK = os.environ.get("SLACK_WEBHOOK_URL")
LOG = init_logger(os.environ.get("LOG_LEVEL"))


class OrderConfirmationException(Exception):
    """Base class for order confirmation exceptions"""


class OrderConfirmation:
    """Class for sending a confirmation email for a merch order"""

    slack_channel = os.environ.get("SLACK_ORDERS_CHANNEL")
    slack_webhook_url = os.environ.get("SLACK_ORDERS_WEBHOOK_URL", DEFAULT_WEBHOOK)
    support_email = os.environ.get("SUPPORT_EMAIL_ADDRESS")
    support_phone = os.environ.get("SUPPORT_PHONE_NUMBER")
    shipping_price = os.environ.get("SHIPPING_PRICE", 6.99)
    subject = "Beantown Pub Merch Order Confirmation"
    sender = "Beantown Merch <orders@beantownpub.com>"

    def __init__(self, order_info, recipient=None):
        self.order_info = order_info
        self.recipient = recipient if recipient else order_info["order"]["email"]
        self.order_id = order_info["payment"]["order_id"]
        self.order_items = order_info["order"]["cart"]["cart_items"]
        self.items_total = order_info["order"]["cart"]["total"]
        self.order_total = round(self.items_total + self.shipping_price, 2)

    def _parse_items(self):
        if not self.order_items:
            raise OrderConfirmationException("No items in this order %s", self.order_id)
        item_html = []
        for item in self.order_items:
            if item.get("size"):
                item_html.append(
                    f"<tr><td>{item['name']}</td><td>{item['size']}</td><td>{item['quantity']}</td><td>{item['price']}</td><td>{item['total']}</td></tr>"
                )
            else:
                item_html.append(
                    f"<tr><td>{item['name']}</td><td></td><td>{item['quantity']}</td><td>{item['price']}</td><td>{item['total']}</td></tr>"
                )
        return "\n".join(item_html)

    def _shipping_address(self):
        street = self.order_info["order"]["street"]
        unit = self.order_info["order"]["unit"]
        city = self.order_info["order"]["city"]
        state = self.order_info["order"]["state"]
        zip = self.order_info["order"]["zipCode"]
        address = """
        <p>{}<br />
        {} <br />
        {}, {}, {}
        </p>
        """.format(
            street, unit, city, state, zip
        )
        return address

    def _build_body(self):
        body = confirmation_email.format(
            self.order_id,
            self._parse_items(),
            self.items_total,
            self.shipping_price,
            self.order_total,
            self._shipping_address(),
            self.support_email,
            self.support_phone,
        )
        return body

    def _build_raw_text(self):
        """Build plain text message"""
        body_text = [
            f"Confirmation code: {self.order_id}",
            f"Items: {self.order_items}",
            f"Order total: {self.order_total}",
            "Questions?",
            f"Email: {self.support_email}",
            f"Call: {self.support_phone}",
        ]
        return "\n".join(body_text)

    def send_email(self):
        LOG.info("Sending order confirmation email to %s", self.recipient)
        send_message(
            self.recipient,
            self._build_body(),
            self._build_raw_text(),
            self.subject,
            self.sender,
        )

    def send_slack(self):
        """Send message to Slack"""
        if self.order_info["order"]["lastName"] == "Ordertester-123":
            slack_url = DEFAULT_WEBHOOK
        else:
            slack_url = self.slack_webhook_url
        response = slack_message(
            self.slack_channel, self.order_info, slack_url
        )
        return response


class EventRequest:
    """Class for sending an email for a private event request"""

    sender = "Beantown Event <contact@beantownpub.com>"
    slack_channel = os.environ.get("SLACK_PARTYS_CHANNEL")
    slack_webhook_url = os.environ.get("SLACK_PARTYS_WEBHOOK_URL", DEFAULT_WEBHOOK)

    def __init__(self, contact_info, recipient):
        self.contact_info = add_creation_date(contact_info)
        self.location = contact_info["location"]
        self.name = contact_info["name"]
        self.phone_number = contact_info["phone"]
        self.email = contact_info["email"]
        self.details = contact_info["details"]
        self.catering = contact_info["catering"]
        self.recipient = recipient

    def _build_subject(self):
        subject = f"{self.location.title()} Private Event Contact"
        return subject

    def _build_body(self):
        body = event_request_html.format(
            self.location.title(),
            self.name,
            self._format_phone_number(),
            self.email,
            self.details,
            self.catering,
        )
        return body

    def _format_phone_number(self):
        number = self.phone_number
        if len(number) == 10:
            number = f"{number[0:3]}-{number[3:6]}-{number[6:]}"
        return number

    def _build_raw_text(self):
        """Build plain text message"""
        raw_text = event_request_raw.format(
            self.location.title(),
            self.name,
            self._format_phone_number(),
            self.email,
            self.details,
            self.catering,
        )
        return raw_text

    def send_email(self):
        LOG.info("Sending AWS Email from %s", self.sender)
        send_message(
            self.recipient,
            self._build_body(),
            self._build_raw_text(),
            self._build_subject(),
            self.sender,
        )

    def send_slack(self):
        """Send message to Slack"""
        LOG.info("Sending Slack message | %s", self.contact_info)
        if self.contact_info["name"] == "Partytester-123":
            slack_url = DEFAULT_WEBHOOK
        else:
            slack_url = self.slack_webhook_url
        response = slack_message(
            self.slack_channel, self.contact_info, slack_url
        )
        return response
