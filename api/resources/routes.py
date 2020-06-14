from .contact import ContactAPI


def init_routes(api):
    api.add_resource(ContactAPI, '/v1/contact/<location>')
