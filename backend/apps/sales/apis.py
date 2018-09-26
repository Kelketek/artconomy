import dwollav2
from authorize import AuthorizeClient
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.utils.datetime_safe import datetime
from lazy import lazy


sauce = AuthorizeClient(settings.AUTHORIZE_KEY, settings.AUTHORIZE_SECRET, debug=settings.SANDBOX_APIS)
client = dwollav2.Client(
    key=settings.DWOLLA_KEY,
    secret=settings.DWOLLA_SECRET,
    environment='sandbox' if settings.SANDBOX_APIS else 'production'
)


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
        if self.timestamp and self.timestamp > (datetime.now() - relativedelta(minutes=30)):
            return self.token
        self.token = client.Auth.client()
        self.timestamp = datetime.now()
        return self.token

    def __enter__(self):
        return self.dwolla_api

    def __exit__(self, exc_type, exc_val, exc_tb):
        return


dwolla = DwollaContext()
