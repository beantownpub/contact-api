from datetime import datetime


def add_creation_date(message_body):
        created = datetime.strftime(datetime.today(), "%m-%d-%Y %H:%M")
        message_body['created'] = created
        return message_body
