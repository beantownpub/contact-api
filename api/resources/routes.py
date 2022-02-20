from .contact import EventContactAPI, MerchContactAPI
from .healthcheck import HealthCheckAPI
from .slack import SlackAPI


def init_routes(api):
    api.add_resource(EventContactAPI, "/v1/contact/<location>")
    api.add_resource(MerchContactAPI, "/v1/contact/merch")
    api.add_resource(HealthCheckAPI, "/v1/contact/healthz")
    api.add_resource(SlackAPI, "/v1/contact/slack")
