from typing import List, Optional, Tuple, TypedDict

import pycountry
import stripe as stripe_api
from django.conf import settings
from moneyed import Money


class StripeContext:
    def __init__(self):
        self.stripe = stripe_api

    def __enter__(self):
        self.stripe.api_key = settings.STRIPE_KEY
        return self.stripe

    def __exit__(self, exc_type, exc_val, exc_tb):
        return


stripe = StripeContext()


def delete_payment_method(*, api: stripe_api, method_token: str):
    api.PaymentMethod.detach(
        method_token,
    )


def money_to_stripe(money: Money) -> Tuple[int, str]:
    amount = int(money.amount * money.currency.sub_unit)
    return amount, money.currency.code.lower()


def refund_payment_intent(*, api: stripe_api, intent_token: str, amount: Money):
    amount = money_to_stripe(amount)[0]
    return api.Refund.create(
        amount=amount,
        payment_intent=intent_token,
    )


def cancel_payment_intent(*, api: stripe_api, intent_token: str):
    return api.PaymentIntent.cancel(intent_token)


def create_stripe_account(*, api: stripe_api, country: str):
    data = {
        "type": "express",
        "country": country,
        "capabilities": {
            "transfers": {
                "requested": True,
            }
        },
    }
    if country != "US":
        data["tos_acceptance"] = {
            "service_agreement": "recipient",
        }
    return api.Account.create(
        **data,
    )


def create_account_link(
    *, api: stripe_api, refresh_url: str, return_url: str, token: str
):
    return api.AccountLink.create(
        type="account_onboarding",
        return_url=return_url,
        refresh_url=refresh_url,
        account=token,
    )


class CountrySpec(TypedDict):
    value: str
    title: str


class CountryCache(TypedDict):
    cache: Optional[List[CountrySpec]]


COUNTRY_CACHE: CountryCache = {"cache": None}


def get_country_list(*, api: stripe_api) -> List[CountrySpec]:
    if COUNTRY_CACHE["cache"] is not None:
        return COUNTRY_CACHE["cache"]
    specs = api.CountrySpec.retrieve(id="US")
    countries = []
    for country_code in specs["supported_transfer_countries"]:
        countries.append(
            {
                "value": country_code,
                "title": pycountry.countries.get(alpha_2=country_code).name,
            }
        )
    countries.sort(key=lambda country: country["title"])
    COUNTRY_CACHE["cache"] = countries
    return COUNTRY_CACHE["cache"]


def remote_ids_from_charge(charge_event):
    return [charge_event["payment_intent"], charge_event["id"]]
