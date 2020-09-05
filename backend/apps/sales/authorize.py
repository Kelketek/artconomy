import logging
import re
import traceback
from collections import namedtuple, OrderedDict
from decimal import Decimal
from typing import TypedDict, Any

from authorizenet import apicontractsv1
from authorizenet.apicontrollers import (
    createCustomerProfileController, createCustomerPaymentProfileController,
    deleteCustomerPaymentProfileController,
    createTransactionController,
    createCustomerProfileFromTransactionController, getTransactionDetailsController)
from authorizenet.apicontrollersbase import APIOperationBase
from authorizenet.constants import constants
from django.conf import settings
from lxml.etree import tostring
from moneyed import Money

logger = logging.getLogger(__name__)


RESPONSE_TRANSLATORS = {
    '54': 'This transaction cannot be refunded. It may not yet have posted. '
          'Please try again tomorrow, and contact support if it still fails.',
    'E00027': "The zip or address we have on file for your card is either incorrect or has changed. Please remove the "
              "card and add it again with updated information.",
    'E00040': "Something is wrong in our records with the card you've added. Please remove the card and re-add it.",
}


class AuthorizeException(Exception):
    """
    Used any time we have an issue performing a transaction with Authorize.net
    """
    def __init__(self, *args, code=None):
        self.code = code
        super().__init__(*args)


def authenticate() -> apicontractsv1.merchantAuthenticationType:
    """
    Generates the authentication stub needed for all requests.
    """
    merchant_auth = apicontractsv1.merchantAuthenticationType()
    merchant_auth.name = settings.AUTHORIZE_KEY
    merchant_auth.transactionKey = settings.AUTHORIZE_SECRET
    return merchant_auth


class CardInfo(namedtuple('CardInfo', ['number', 'exp_year', 'exp_month', 'cvv'])):
    def fixture(self):
        credit_card = apicontractsv1.creditCardType()
        credit_card.cardNumber = self.number
        credit_card.expirationDate = "{}-{}".format(self.exp_year, str(self.exp_month).zfill(2))
        credit_card.cardCode = self.cvv
        return credit_card


class AddressInfo(namedtuple(
    'AddressInfo', ['first_name', 'last_name', 'country', 'postal_code']
)):
    def fixture(self):
        address = apicontractsv1.customerAddressType()
        address.firstName = self.first_name
        address.lastName = self.last_name
        address.country = self.country
        address.state = 'XX'
        address.address = 'Unspecified'
        address.city = 'Unspecified'
        address.zip = self.postal_code
        return address

tag_name_pattern = re.compile(r'[{].*[}](.*)')


def tag_text(tag, level: int) -> str:  #pragma: no cover
    tag_name = tag_name_pattern.match(tag.tag)[1]
    text = (' ' * level * 2) + f'[{tag_name}]: ' + tag.text + '\n'
    return text


MockCustomerProfileResponse = namedtuple('MockCustomerProfileResponse', ('customerProfileId',))

def has_transaction_error(response):
    return hasattr(response, 'transactionResponse') and hasattr(response.transactionResponse, 'errors')


def execute(controller: APIOperationBase):
    """
    Wrapper for authorize.net controllers that raises a proper exception if there's an issue, and contacts either
    the production or sandbox endpoints depending on configuration.
    """
    if not settings.SANDBOX_APIS:
        controller.setenvironment(constants.PRODUCTION)
    try:
        controller.execute()
    except Exception as err:
        traceback.print_exc()
        raise AuthorizeException(str(err))
    response = controller.getresponse()
    if not response.messages.resultCode == "Ok":
        if response.messages.message[0]['code'].text == 'E00039':
            # Duplicate profile record.
            # Should contain the payment ID of the intended customer, so pass it along.
            # A duplicate record with ID 1919640746 already exists.
            profile_id = re.match(
                r'A duplicate record with ID ([0-9]+) already exists[.]', response.messages.message[0]['text'].text,
            )[1]
            return MockCustomerProfileResponse(customerProfileId=profile_id)
        logger.error("Authorize.net failure. %s", ''.join(traceback.format_stack()))
        logger.error(tostring(response, pretty_print=True).decode('utf-8'))
        code, response = translate_authnet_error(response)
        raise AuthorizeException(
            response, code=code,
        )
    # Can still be OK but have an error at a higher level.
    if has_transaction_error(response):
        code, response = translate_authnet_error(response)
        raise AuthorizeException(
            response, code=code,
        )
    return response


def create_customer_profile(email) -> str:
    """
    Makes sure we have a customer profile for this user on Authorize.net's servers.
    """
    init_customer_profile = apicontractsv1.createCustomerProfileRequest()
    init_customer_profile.merchantAuthentication = authenticate()
    init_customer_profile.profile = apicontractsv1.customerProfileType()
    init_customer_profile.profile.email = email

    controller = createCustomerProfileController(init_customer_profile)
    response = execute(controller)
    return str(response.customerProfileId)


def create_card(card_info: CardInfo, address_info: AddressInfo, profile_id: str) -> str:
    """
    Takes credit card information and saves it for later use.
    """
    request = apicontractsv1.createCustomerPaymentProfileRequest()
    request.merchantAuthentication = authenticate()
    request.paymentProfile = apicontractsv1.customerPaymentProfileType()
    request.paymentProfile.payment = apicontractsv1.paymentType()
    request.paymentProfile.payment.creditCard = card_info.fixture()
    request.paymentProfile.billTo = address_info.fixture()
    request.customerProfileId = profile_id
    # Creates either a 0 cent or 1 cent test authorization, immediately reversed, to validate CVV.
    request.validationMode = 'liveMode'
    controller = createCustomerPaymentProfileController(request)
    response = execute(controller)
    return response.customerPaymentProfileId


class TransactionDetails(TypedDict):
    auth_code: str
    auth_amount: Money


def transaction_details(remote_id: str) -> TransactionDetails:
    request = apicontractsv1.getTransactionDetailsRequest()
    request.merchantAuthentication = authenticate()
    request.transId = remote_id

    controller = getTransactionDetailsController(request)
    transaction = execute(controller).transaction

    return {
        'auth_code': to_authcode(transaction.authCode),
        'auth_amount': Money(str(transaction.authAmount), 'USD'),
    }


def charge_card(card_info: CardInfo, address_info: AddressInfo, amount: Decimal, ip=None) -> (str, str):
    transaction_request = apicontractsv1.transactionRequestType()
    transaction_request.amount = amount
    transaction_request.transactionType = "authCaptureTransaction"
    transaction_request.payment = apicontractsv1.paymentType()
    transaction_request.payment.creditCard = card_info.fixture()
    transaction_request.billTo = address_info.fixture()
    if ip:
        transaction_request.customerIP = ip

    create_transaction_request = apicontractsv1.createTransactionRequest()
    create_transaction_request.merchantAuthentication = authenticate()
    create_transaction_request.transactionRequest = transaction_request

    controller = createTransactionController(
        create_transaction_request)
    response = execute(controller)
    return str(response.transactionResponse.transId), to_authcode(response.transactionResponse.authCode)


def card_token_from_transaction(transaction_id: str, profile_id: str) -> str:
    profile_from_transaction = apicontractsv1.createCustomerProfileFromTransactionRequest()
    profile_from_transaction.merchantAuthentication = authenticate()
    profile_from_transaction.transId = transaction_id
    profile_from_transaction.customerProfileId = profile_id

    controller = createCustomerProfileFromTransactionController(profile_from_transaction)
    response = execute(controller)
    return response.customerPaymentProfileIdList[0].numericString


def charge_saved_card(
        profile_id: str = None, payment_id: str = None, amount: Decimal = None, cvv=None, ip=None,
) -> (str, str):
    """
    Creates an authorization/capture for a card.
    """
    if not all([profile_id, payment_id, amount]):
        fields = OrderedDict(sorted(list(locals().items())))
        raise ValueError(f'Did not provide all required fields! {fields}')
    # create a customer payment profile
    profile = apicontractsv1.customerProfilePaymentType()
    profile.customerProfileId = profile_id
    profile.cardCode = cvv
    profile.paymentProfile = apicontractsv1.paymentProfile()
    profile.paymentProfile.paymentProfileId = payment_id

    transaction_request = apicontractsv1.transactionRequestType()
    transaction_request.transactionType = "authCaptureTransaction"
    transaction_request.amount = amount
    transaction_request.profile = profile
    if ip:
        transaction_request.customerIP = ip

    create_transaction_request = apicontractsv1.createTransactionRequest()
    create_transaction_request.merchantAuthentication = authenticate()

    create_transaction_request.transactionRequest = transaction_request
    controller = createTransactionController(create_transaction_request)

    response = execute(controller).transactionResponse

    return str(response.transId), to_authcode(response.authCode)


def delete_card(profile_id: str = None, payment_id: str = None):
    request = apicontractsv1.deleteCustomerPaymentProfileRequest()
    request.merchantAuthentication = authenticate()
    request.customerProfileId = profile_id
    request.customerPaymentProfileId = payment_id
    controller = deleteCustomerPaymentProfileController(request)
    try:
        execute(controller)
    except AuthorizeException as err:
        if err.code != 'E00040':
            raise
        # Record not found-- in other words, it's not on their servers.
        logger.warning(
            f"Could not find card token %s on Authorize.net's servers: {profile_id} {payment_id}",
        )


def refund_transaction(txn_id: str, last_four: str, amount: Decimal):
    card = apicontractsv1.creditCardType()
    card.cardNumber = last_four
    card.expirationDate = 'XXXX'

    payment = apicontractsv1.paymentType()
    payment.creditCard = card

    transaction = apicontractsv1.transactionRequestType()
    transaction.transactionType = "refundTransaction"
    transaction.amount = amount
    transaction.refTransId = txn_id
    transaction.payment = payment

    request = apicontractsv1.createTransactionRequest()
    request.merchantAuthentication = authenticate()

    request.transactionRequest = transaction
    controller = createTransactionController(request)
    response = execute(controller)
    return str(response.transactionResponse.transId), to_authcode(response.transactionResponse.authCode)


def derive_authnet_error(err):
    if has_transaction_error(err):
        error = err.transactionResponse.errors[0].error
        return error.errorCode.text, error.errorText.text
    return err.messages.message[0]['code'].text, err.messages.message[0]['text'].text


def translate_authnet_error(err):
    code, text = derive_authnet_error(err)
    return code, RESPONSE_TRANSLATORS.get(code, text)

# from https://github.com/drewisme/authorizesauce MIT License
CARD_TYPES = {
    'visa': r'4\d{12}(\d{3})?$',
    'amex': r'37\d{13}$',
    'mc': r'5[1-5]\d{14}$',
    'discover': r'6011\d{12}',
    'diners': r'(30[0-5]\d{11}|(36|38)\d{12})$'
}

def get_card_type(number):
    """
    The credit card issuer, such as Visa or American Express, which is
    determined from the credit card number. Recognizes Visa, American
    Express, MasterCard, Discover, and Diners Club.
    """
    for card_type, card_type_re in CARD_TYPES.items():
        if re.match(card_type_re, number):
            return card_type


def to_authcode(value: Any) -> str:
    value = str(value)
    if not value:
        return ''
    return value.zfill(6)
