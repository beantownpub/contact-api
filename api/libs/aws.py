import os
import boto3
from botocore.exceptions import ClientError

from api.libs.logging import init_logger

LOG = init_logger(os.environ.get('LOG_LEVEL'))
AWS_REGION = os.environ.get('AWS_DEFAULT_REGION')
CHARSET = "UTF-8"

client = boto3.client('ses', region_name=AWS_REGION)

def send_message(recipient, body, text, subject, sender):
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
