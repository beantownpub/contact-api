import os
import smtplib


def smtp_send_email(body):
    name = body.get('name', 'Not Provided')
    phone = body.get('phone', 'Not Provided')
    email = body.get('email', 'Not Provided')
    event_date = body.get('event_date', 'Not Provided')
    details = body.get('details', 'Not Provided')
    location = body.get('location', 'Not Provided')
    sender = os.environ.get('EMAIL_SENDER')
    recipient = os.environ.get('EMAIL_RECIPIENT')
    body = [
        f'From: {sender}',
        f'To: {recipient}',
        f'Subject: Private Event Request for {location}\n',
        f'Hello,\n\nYou have a new private event information request from {location}\n',
        'Event Info:\n',
        f'Name: {name}',
        f'Phone: {phone}',
        f'Email: {email}',
        f'Date: {event_date}',
        f'Details: {details}'
    ]
    password = os.environ.get('CONTACT_GMAIL_PASSWORD')
    message = "\n".join(body).encode()
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(sender, password)
    server.sendmail(sender, recipient, message)
    server.close()
