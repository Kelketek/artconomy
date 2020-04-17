from _decimal import Decimal
from unittest import TestCase
from unittest.mock import Mock, MagicMock, patch

from django.test import override_settings

from apps.sales.authorize import (
    authenticate, execute, AuthorizeException, create_customer_profile, AddressInfo,
    CardInfo,
    create_card,
    charge_saved_card,
    refund_transaction,
    delete_card,
)


class TestAuthorize(TestCase):
    @override_settings(AUTHORIZE_KEY='1234', AUTHORIZE_SECRET='5678')
    def test_authenticate(self):
        data = authenticate()
        self.assertEqual(data.name, '1234')
        self.assertEqual(data.transactionKey, '5678')

    @override_settings(SANDBOX_APIS=True)
    def test_execute(self):
        controller = Mock()
        controller.getresponse.return_value.messages.resultCode = 'Ok'
        controller.getresponse.return_value.transactionResponse = None
        execute(controller)
        self.assertTrue(controller.execute.called)
        self.assertTrue(controller.getresponse.called)
        self.assertFalse(controller.setenvironment.called)

    @override_settings(SANDBOX_APIS=False)
    def test_execute_production(self):
        controller = Mock()
        controller.getresponse.return_value.messages.resultCode = 'Ok'
        controller.getresponse.return_value.transactionResponse = None
        execute(controller)
        self.assertTrue(controller.execute.called)
        self.assertTrue(controller.getresponse.called)
        controller.setenvironment.assert_called_with('https://api2.authorize.net/xml/v1/request.api')

    @patch('traceback.print_exc')
    def test_execute_exception_raised(self, mock_print_exec):
        controller = Mock()
        controller.execute.side_effect = RuntimeError('Failed.')
        with self.assertRaises(AuthorizeException) as cm:
            execute(controller)
        self.assertEqual(str(cm.exception), 'Failed.')
        self.assertTrue(mock_print_exec.called)

    @patch('apps.sales.authorize.tostring')
    def test_execute_raise_failure(self, mock_to_string):
        mock_to_string.return_value = b'test'
        controller = Mock()
        message = {
            'text': Mock(),
            'code': Mock(),
        }
        message['text'].text = 'Lame.'
        message['code'].text = 'Code Red'
        controller.execute = MagicMock()
        controller.getresponse = Mock()
        response = Mock(spec=['messages'])
        response.messages.message = [message]
        controller.getresponse.return_value = response
        with self.assertRaises(AuthorizeException) as cm:
            execute(controller)
        self.assertEqual(cm.exception.code, 'Code Red')
        self.assertEqual(str(cm.exception), 'Lame.')
        mock_to_string.assert_called_with(response, pretty_print=True)

    @patch('apps.sales.authorize.execute')
    def test_create_customer_profile(self, mock_execute):
        mock_execute.return_value.customerProfileId = '123'
        token = create_customer_profile('test@example.com')
        self.assertTrue(mock_execute.called)
        self.assertEqual(token, '123')

    @patch('apps.sales.authorize.execute')
    def test_create_card(self, mock_execute):
        address_info = AddressInfo(
            first_name='Jim',
            last_name='Bob',
            postal_code='77079',
            country='USA',
        )
        card_info = CardInfo(
            number='4111111111111111',
            cvv='555',
            exp_month=8,
            exp_year=2020,
        )
        mock_execute.return_value.customerPaymentProfileId = '456'
        payment_id = create_card(card_info, address_info, '345')
        self.assertEqual(payment_id, '456')

    # We're going to end up relying on the XML validation for these next few tests.
    @patch('apps.sales.authorize.execute')
    def test_charge_card(self, mock_execute):
        charge_saved_card(profile_id='1234', payment_id='5678', amount=Decimal('10.00'))
        self.assertTrue(mock_execute.called)

    # We're going to end up relying on the XML validation for these next few tests.
    @patch('apps.sales.authorize.execute')
    def test_charge_card_with_ip(self, mock_execute):
        charge_saved_card(profile_id='1234', payment_id='5678', amount=Decimal('10.00'), ip='127.0.0.1')
        self.assertTrue(mock_execute.called)

    @patch('apps.sales.authorize.execute')
    def test_charge_card_missing_params(self, _mock_execute):
        with self.assertRaises(ValueError) as cm:
            charge_saved_card(payment_id='5678', amount=Decimal('10.00'))
        self.assertEqual(
            str(cm.exception),
            "Did not provide all required fields! "
            "OrderedDict([('amount', Decimal('10.00')), ('cvv', None), "
            "('ip', None), ('payment_id', '5678'), ('profile_id', None)])"
        )

    @patch('apps.sales.authorize.execute')
    def test_refund_transaction(self, mock_execute):
        mock_execute.return_value.transactionResponse.transId = '1234'
        mock_execute.return_value.transactionResponse.authCode = 'ABC123'
        remote_id, auth_code = refund_transaction('1234567', '1111', Decimal('5.00'))
        self.assertEqual(remote_id, '1234')
        self.assertEqual(auth_code, 'ABC123')

    @patch('apps.sales.authorize.execute')
    def test_delete_card(self, mock_execute):
        delete_card('1234', '5435')
        self.assertTrue(mock_execute.called)

    @patch('apps.sales.authorize.logger')
    @patch('apps.sales.authorize.execute')
    def test_delete_card_missing(self, mock_execute, mock_logger):
        mock_execute.side_effect = AuthorizeException('Missing', code='E00040')
        delete_card('1234', '5435')
        self.assertTrue(mock_execute.called)
        mock_logger.warning.assert_called_with("Could not find card token %s on Authorize.net's servers: 1234 5435")

    @patch('apps.sales.authorize.execute')
    def test_delete_card_other_problem(self, mock_execute):
        mock_execute.side_effect = AuthorizeException('Other')
        with self.assertRaises(AuthorizeException):
            delete_card('1234', '5435')
