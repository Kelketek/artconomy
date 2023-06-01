from typing import Union
from unittest.mock import Mock
from urllib.parse import urljoin

import requests
from django.conf import settings
from mailchimp3 import MailChimp
from requests import Session


def init_chimp() -> Union[MailChimp, Mock]:
    if settings.MAILCHIMP_API_KEY:
        headers = requests.utils.default_headers()
        headers["User-Agent"] = settings.USER_AGENT
        return MailChimp(
            mc_api=settings.MAILCHIMP_API_KEY, timeout=10.0, request_headers=headers
        )
    else:
        return Mock()


class DripSession(Session):
    def __init__(self, base_url="https://api.getdrip.com/"):
        self.base_url = base_url
        super().__init__()

    def request(self, method, url, *args, **kwargs):
        joined_url = urljoin(self.base_url, url)
        return super().request(method, joined_url, *args, **kwargs)


def init_drip() -> DripSession:
    if settings.DRIP_API_KEY and settings.DRIP_ACCOUNT_KEY:
        drip_session = DripSession()
        drip_session.headers.update({"User-Agent": settings.USER_AGENT})
        drip_session.auth = (settings.DRIP_API_KEY, "")
        return drip_session
    return Mock(spec=DripSession)


chimp = init_chimp()

drip = init_drip()
