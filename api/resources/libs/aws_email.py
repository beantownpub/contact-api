import os
import boto3
from botocore.exceptions import ClientError

from api.libs.logging import init_logger
from api.libs.templates import confirmation_email

LOG = init_logger(os.environ.get('LOG_LEVEL'))
AWS_REGION = os.environ.get('AWS_DEFAULT_REGION')
CHARSET = "UTF-8"

class OrderConfirmationException(Exception):
    """Base class for order confirmation exceptions"""


client = boto3.client('ses', region_name=AWS_REGION)


def _send_message(recipient, body, text, subject, sender):
    LOG.info('_send_message sending email to %s from %s', recipient, sender)
    second_recipient = os.environ.get("SECOND_EMAIL_RECIPIENT")
    if second_recipient:
        recipients = [recipient, second_recipient, ]
    else:
        recipients = [recipient, ]
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': recipients
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': body,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': text,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            Source=sender,
        )
    except ClientError as e:
        LOG.error('AWS Error: %s', e)
    LOG.info('- AWS response: %s', response)
    return response


class OrderConfirmation:
    """Class for sending a confirmation email for a merch order
    """
    support_email = os.environ.get('SUPPORT_EMAIL_ADDRESS')
    support_phone = os.environ.get('SUPPORT_PHONE_NUMBER')
    shipping_price = os.environ.get('SHIPPING_PRICE', 6.99)
    subject = "Beantown Pub Merch Order Confirmation"
    sender = "Beantown Merch <orders@beantownpub.com>"

    def __init__(self, order_info):
        self.order_info = order_info
        self.recipient = order_info["order"]["email"]
        self.order_id = order_info["payment"]["order_id"]
        self.order_items = order_info["order"]["cart"]["cart_items"]
        self.items_total = order_info["order"]["cart"]["total"]
        self.order_total = round(self.items_total + self.shipping_price, 2)

    def _parse_items(self):
        if not self.order_items:
            raise OrderConfirmationException("No items in this order %s", self.order_id)
        item_html = []
        for item in self.order_items:
            if item.get('size'):
                item_html.append(f"<tr><td>{item['name']}</td><td>{item['size']}</td><td>{item['quantity']}</td><td>{item['price']}</td><td>{item['total']}</td></tr>")
            else:
                item_html.append(f"<tr><td>{item['name']}</td><td></td><td>{item['quantity']}</td><td>{item['price']}</td><td>{item['total']}</td></tr>")
        return "\n".join(item_html)


    def _build_body(self):
        body = confirmation_email.format(
                self.order_id,
                self._parse_items(),
                self.items_total,
                self.shipping_price,
                self.order_total,
                self.support_email,
                self.support_phone
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
            f"Call: {self.support_phone}"
        ]
        return "\n".join(body_text)

    def send_message(self):
        LOG.info("Sending order confirmation email to %s", self.recipient)
        _send_message(
            self.recipient,
            self._build_body(),
            self._build_raw_text(),
            self.subject,
            self.sender
        )


class EventRequest:
    """Class for sending an email for a private event request
    """

    sender = "Beantown Event <contact@beantownpub.com>"

    def __init__(self, contact_info, recipient):
        self.contact_info = contact_info
        self.recipient = recipient

    def _build_subject(self):
        location = self.contact_info.get('location')
        subject = f"{location.title()} Private Event Contact"
        return subject

    def _build_body(self):
        info = self.contact_info
        if len(info['phone_number']) == 10:
            info['phone_number'] = f"{info['phone_number'][0:3]}-{info['phone_number'][3:6]}-{info['phone_number'][6:]}"
        body = f"""<html>
        <head></head>
        <body>
            <h3>{info['location'].title()} Private Event Contact</h3>
            <table>
                <tr><td><strong>Name:</strong></td><td>{info['name']}</td></tr>
                <tr><td><strong>Phone:</strong></td><td>{info['phone_number']}</td></tr>
                <tr><td><strong>Email:</strong></td><td>{info['email']}</td></tr>
                <tr><td><strong>Details:</strong></td><td>{info['details']}</td></tr>
                <tr><td><strong>Catering:</strong></td><td>{info['catering']}</td></tr>
            </table>
        </body>
        </html>
        """
        return body

    def _build_raw_text(self):
        """Build plain text message"""

        body_text = [
            f"{self.contact_info['location'].title()} Event Contact",
            f"Name: {self.contact_info['name']}",
            f"Phone: {self.contact_info['phone_number']}",
            f"Email: {self.contact_info['email']}",
            f"Details: {self.contact_info['details']}",
            f"Catering: {self.contact_info['catering']}"
        ]
        return "\n".join(body_text)

    def send_message(self):
        LOG.info('Sending AWS Email from %s', self.sender)
        _send_message(
            self.recipient,
            self._build_body(),
            self._build_raw_text(),
            self._build_subject(),
            self.sender
        )
