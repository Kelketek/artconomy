from typing import Union
from unittest.mock import Mock

import requests
from django.conf import settings
from mailchimp3 import MailChimp


def init_chimp() -> Union[MailChimp, Mock]:
    if settings.MAILCHIMP_API_KEY:
        headers = requests.utils.default_headers()
        headers['User-Agent'] = 'Artconomy (fox@artconomy.com)'
        return MailChimp(mc_api=settings.MAILCHIMP_API_KEY, timeout=10.0, request_headers=headers)
    else:
        return Mock()


chimp = init_chimp()
