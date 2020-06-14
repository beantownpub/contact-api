import os

from api.app import APP


if __name__ == "__main__":
    APP.config.from_object(__name__)
    if os.environ.get('CONTACT_API_DEBUG'):
        APP.debug = True
    APP.run()
