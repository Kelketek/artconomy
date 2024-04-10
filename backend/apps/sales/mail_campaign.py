from unittest.mock import Mock
from urllib.parse import urljoin

from django.conf import settings
from requests import Session


class DripSession(Session):
    def __init__(self, base_url="https://api.getdrip.com/"):
        self.base_url = base_url
        super().__init__()

    def request(self, method, url, *args, **kwargs):
        joined_url = urljoin(self.base_url, url)
        return super().request(method, joined_url, *args, **kwargs)


def init_drip() -> DripSession:
    if settings.DRIP_API_KEY and settings.DRIP_ACCOUNT_ID:
        drip_session = DripSession()
        drip_session.headers.update({"User-Agent": settings.USER_AGENT})
        drip_session.auth = (settings.DRIP_API_KEY, "")
        return drip_session
    return Mock(spec=DripSession)


drip = init_drip()
