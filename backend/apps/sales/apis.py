from typing import Union
from unittest.mock import Mock

import dwollav2
import requests
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.utils import timezone
from lazy import lazy
from mailchimp3 import MailChimp


def create_client() -> dwollav2.Client:
    return dwollav2.Client(
        key=settings.DWOLLA_KEY,
        secret=settings.DWOLLA_SECRET,
        environment='sandbox' if settings.SANDBOX_APIS else 'production'
    )


def init_chimp() -> Union[MailChimp, Mock]:
    if settings.MAILCHIMP_API_KEY:
        headers = requests.utils.default_headers()
        headers['User-Agent'] = 'Artconomy (fox@artconomy.com)'
        return MailChimp(mc_api=settings.MAILCHIMP_API_KEY, timeout=10.0, request_headers=headers)
    else:
        return Mock()


client = create_client()

chimp = init_chimp()


class DwollaContext:
    def __init__(self):
        self.timestamp = None
        self.token = None
        self.source_url = ''

    @lazy
    def funding_url(self):
        return settings.DWOLLA_FUNDING_SOURCE_KEY

    @lazy
    def account_url(self):
        root = self.dwolla_api.get('/')
        return root.body['_links']['account']['href']

    @property
    def dwolla_api(self):
        if self.timestamp and self.timestamp > (timezone.now() - relativedelta(minutes=30)):
            return self.token
        self.token = client.Auth.client()
        self.timestamp = timezone.now()
        return self.token

    def __enter__(self):
        return self.dwolla_api

    def __exit__(self, exc_type, exc_val, exc_tb):
        return


dwolla = DwollaContext()


AUTHORIZE = 'authorize'
STRIPE = 'stripe'

PROCESSOR_CHOICES = (
    (AUTHORIZE, 'EVO Authorize.net'),
    (STRIPE, 'Stripe'),
)
