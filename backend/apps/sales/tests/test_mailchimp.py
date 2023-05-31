from unittest import TestCase
from unittest.mock import Mock, patch

from apps.sales.mail_campaign import init_chimp
from django.test import override_settings
from requests.structures import CaseInsensitiveDict


class TestInitChimp(TestCase):
    @override_settings(MAILCHIMP_API_KEY="")
    @patch("apps.sales.mail_campaign.MailChimp")
    def test_init_chimp_dummy(self, mock_mail_chimp):
        target = Mock()
        mock_mail_chimp.return_value = target
        self.assertIsNot(init_chimp(), target)
        mock_mail_chimp.assert_not_called()

    @override_settings(MAILCHIMP_API_KEY="12345")
    @patch("apps.sales.mail_campaign.MailChimp")
    def test_init_chimp_production(self, mock_mail_chimp):
        target = Mock()
        mock_mail_chimp.return_value = target
        self.assertIs(init_chimp(), target)
        expected_headers = CaseInsensitiveDict(
            {
                "User-Agent": "Artconomy (fox@artconomy.com)",
                "Accept-Encoding": ", ".join(("gzip", "deflate")),
                "Accept": "*/*",
                "Connection": "keep-alive",
            }
        )
        mock_mail_chimp.assert_called_with(
            mc_api="12345", timeout=10.0, request_headers=expected_headers
        )
