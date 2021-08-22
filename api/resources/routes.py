from .contact import EventContactAPI, MerchContactAPI


def init_routes(api):
    api.add_resource(EventContactAPI, '/v1/contact/<location>')
    api.add_resource(MerchContactAPI, '/v1/contact/merch')
