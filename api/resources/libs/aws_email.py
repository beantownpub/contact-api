import logging
import os
import boto3
from botocore.exceptions import ClientError

app_log = logging.getLogger()

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app_log.handlers = gunicorn_logger.handlers
    app_log.setLevel('INFO')

AWS_REGION = os.environ.get('AWS_DEFAULT_REGION')
CHARSET = "UTF-8"


client = boto3.client('ses', region_name=AWS_REGION)


def _send_message(recipient, body, text, subject, sender):
    app_log.info('_send_message sending email to %s from %s', recipient, sender)
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
        app_log.error('AWS Error: %s', e)
    app_log.info('- AWS response: %s', response)
    return response


class awsConformationEmail:
    '''Class for sending a confirmation email for a merch order
    '''

    subject = "Beantown Pub Merch Order Confirmation"
    sender = "Beantown Merch <orders@beantownpub.com>"

    def __init__(self, order_id, recipient):
        self.order_id = order_id
        self.recipient = recipient

    def _build_body(self):
        body = """<html>
        <head></head>
        <body>
            <h1>Beantown Pub Merch Order Confirmation</h1>
            <table>
                <tr><td>Order ID</td><td>{}</td></tr>
            </table>
        </body>
        </html>
        """.format(self.order_id)
        return body

    def _build_body_text(self):
        body_text = [
            "Thank you for your order!",
            "Have a nice day!"
        ]
        return body_text

    def send_message(self):
        _send_message(
            self.recipient,
            self._build_body(),
            self._build_body_text(),
            self.subject,
            self.sender
        )


class awsContactEmail:
    sender = "Beantown Event <contact@beantownpub.com>"

    def __init__(self, contact_info, recipient):
        self.contact_info = contact_info
        self.recipient = recipient

    def _build_subject(self):
        location = self.contact_info.get('location')
        if location:
            subject = f"{location.title()} Private Event Contact"
        else:
            subject = "Beantown Private Event Contact"
        return subject

    def _build_body(self):
        info = self.contact_info
        if len(info['phone_number']) == 10:
            info['phone_number'] = f"{info['phone_number'][0:3]}-{info['phone_number'][3:6]}-{info['phone_number'][6:]}"
        body = """<html>
        <head></head>
        <body>
            <h3>Beantown Pub Private Event Contact</h3>
            <table>
                <tr><td><strong>Name:</strong></td><td>{}</td></tr>
                <tr><td><strong>Phone:</strong></td><td>{}</td></tr>
                <tr><td><strong>Email:</strong></td><td>{}</td></tr>
                <tr><td><strong>Details:</strong></td><td>{}</td></tr>
            </table>
        </body>
        </html>
        """.format(info['name'], info['phone_number'], info['email'], info['details'])
        return body

    def _build_body_text(self):
        '''Build plain text message'''

        body_text = [
            "Beantown Event Contact",
            f"Name: {self.contact_info['name']}",
            f"Phone: {self.contact_info['phone_number']}",
            f"Email: {self.contact_info['email']}",
            f"Details: {self.contact_info['details']}"
        ]
        return "\n".join(body_text)

    def send_message(self):
        app_log.info('Sending AWS Email from %s', self.sender)
        _send_message(
            self.recipient,
            self._build_body(),
            self._build_body_text(),
            self._build_subject(),
            self.sender
        )


def main():
    info = {
        "name": "jonny test",
        "phone_number": "5558776543",
        "email": "jonny@test.com",
        "details": "This is a test contact message",
        "location": "beantown"
    }
    email = awsContactEmail(info, 'jalgraves@gmail.com')
    response = email.send_message()
    print(response)


if __name__ == '__main__':
    main()
