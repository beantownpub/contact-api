import json
import os
import boto3
import botocore.session
from botocore.exceptions import ClientError

from api.libs.logging import init_logger

LOG = init_logger(os.environ.get("LOG_LEVEL").strip())
AWS_REGION = os.environ.get("AWS_DEFAULT_REGION").strip()
LOG.info("AWS Region: %s", AWS_REGION)
CHARSET = "UTF-8"

ses_client = boto3.client("ses", region_name=AWS_REGION)

def send_message(recipient, body, text, subject, sender):
    LOG.info("_send_message sending email to %s from %s", recipient, sender)
    second_recipient = os.environ.get("SECONDARY_EMAIL_RECIPIENT")
    if second_recipient:
        recipients = [
            recipient,
            second_recipient,
        ]
    else:
        recipients = [
            recipient,
        ]
    try:
        response = ses_client.send_email(
            Destination={"ToAddresses": recipients},
            Message={
                "Body": {
                    "Html": {
                        "Charset": CHARSET,
                        "Data": body,
                    },
                    "Text": {
                        "Charset": CHARSET,
                        "Data": text,
                    },
                },
                "Subject": {
                    "Charset": CHARSET,
                    "Data": subject,
                },
            },
            Source=sender,
        )
    except ClientError as e:
        LOG.error("AWS Error: %s", e)
    LOG.info("- AWS response: %s", response)
    return response
