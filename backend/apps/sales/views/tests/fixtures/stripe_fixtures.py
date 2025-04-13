# Note: This constant and the one following it must be kept in sync,
# as they are the end-to-end result of a test.
def gen_stripe_countries_output():
    return {
        "default_currency": "usd",
        "id": "US",
        "object": "country_spec",
        "supported_bank_account_currencies": {"usd": ["US"]},
        "supported_payment_currencies": [
            "usd",
            "aed",
            "afn",
            "all",
            "amd",
            "ang",
            "aoa",
            "ars",
            "aud",
            "awg",
            "azn",
            "bam",
            "bbd",
            "bdt",
            "bgn",
            "bif",
            "bmd",
            "bnd",
            "bob",
            "brl",
            "bsd",
            "bwp",
            "byn",
            "bzd",
            "cad",
            "cdf",
            "chf",
            "clp",
            "cny",
            "cop",
            "crc",
            "cve",
            "czk",
            "djf",
            "dkk",
            "dop",
            "dzd",
            "egp",
            "etb",
            "eur",
            "fjd",
            "fkp",
            "gbp",
            "gel",
            "gip",
            "gmd",
            "gnf",
            "gtq",
            "gyd",
            "hkd",
            "hnl",
            "hrk",
            "htg",
            "huf",
            "idr",
            "ils",
            "inr",
            "isk",
            "jmd",
            "jpy",
            "kes",
            "kgs",
            "khr",
            "kmf",
            "krw",
            "kyd",
            "kzt",
            "lak",
            "lbp",
            "lkr",
            "lrd",
            "lsl",
            "mad",
            "mdl",
            "mga",
            "mkd",
            "mmk",
            "mnt",
            "mop",
            "mro",
            "mur",
            "mvr",
            "mwk",
            "mxn",
            "myr",
            "mzn",
            "nad",
            "ngn",
            "nio",
            "nok",
            "npr",
            "nzd",
            "pab",
            "pen",
            "pgk",
            "php",
            "pkr",
            "pln",
            "pyg",
            "qar",
            "ron",
            "rsd",
            "rub",
            "rwf",
            "sar",
            "sbd",
            "scr",
            "sek",
            "sgd",
            "shp",
            "sll",
            "sos",
            "srd",
            "std",
            "szl",
            "thb",
            "tjs",
            "top",
            "try",
            "ttd",
            "twd",
            "tzs",
            "uah",
            "ugx",
            "uyu",
            "uzs",
            "vnd",
            "vuv",
            "wst",
            "xaf",
            "xcd",
            "xof",
            "xpf",
            "yer",
            "zar",
            "zmw",
        ],
        "supported_payment_methods": ["ach", "card", "stripe"],
        "supported_transfer_countries": [
            "US",
            "AE",
            "AR",
            "AT",
            "AU",
            "BE",
            "BG",
            "BO",
            "CA",
            "CH",
            "CI",
            "CL",
            "CO",
            "CR",
            "CY",
            "CZ",
            "DE",
            "DK",
            "DO",
            "EE",
            "EG",
            "ES",
            "FI",
            "FR",
            "GB",
            "GM",
            "GR",
            "HK",
            "HR",
            "HU",
            "ID",
            "IE",
            "IL",
            "IS",
            "IT",
            "JP",
            "KE",
            "KR",
            "LI",
            "LT",
            "LU",
            "LV",
            "MA",
            "MT",
            "MX",
            "MY",
            "NL",
            "NO",
            "NZ",
            "PE",
            "PH",
            "PL",
            "PT",
            "PY",
            "RO",
            "RS",
            "SA",
            "SE",
            "SG",
            "SI",
            "SK",
            "SV",
            "TH",
            "TN",
            "TR",
            "TT",
            "UY",
            "ZA",
            "BD",
            "BJ",
            "JM",
            "MC",
            "NE",
            "SN",
            "AG",
            "BH",
            "GH",
            "GT",
            "GY",
            "KW",
            "LC",
            "MU",
            "NA",
            "SM",
            "AM",
            "BA",
            "OM",
            "PA",
            "AZ",
            "BN",
            "BT",
            "EC",
            "MD",
            "MK",
            "QA",
        ],
        "verification_fields": {
            "company": {
                "additional": [],
                "minimum": [
                    "business_profile.mcc",
                    "business_profile.url",
                    "business_type",
                    "company.address.city",
                    "company.address.line1",
                    "company.address.postal_code",
                    "company.address.state",
                    "company.name",
                    "company.phone",
                    "company.tax_id",
                    "external_account",
                    "relationship.owner",
                    "relationship.representative",
                    "tos_acceptance.date",
                    "tos_acceptance.ip",
                ],
            },
            "individual": {
                "additional": [],
                "minimum": [
                    "business_profile.mcc",
                    "business_profile.url",
                    "business_type",
                    "external_account",
                    "individual.address.city",
                    "individual.address.line1",
                    "individual.address.postal_code",
                    "individual.address.state",
                    "individual.dob.day",
                    "individual.dob.month",
                    "individual.dob.year",
                    "individual.email",
                    "individual.first_name",
                    "individual.id_number",
                    "individual.last_name",
                    "individual.phone",
                    "individual.ssn_last_4",
                    "individual.verification.document",
                    "tos_acceptance.date",
                    "tos_acceptance.ip",
                ],
            },
        },
    }


COUNTRIES_ARTCONOMY_OUTPUT = {
    "countries": [
        {"title": "Antigua and Barbuda", "value": "AG"},
        {"title": "Argentina", "value": "AR"},
        {"title": "Armenia", "value": "AM"},
        {"title": "Australia", "value": "AU"},
        {"title": "Austria", "value": "AT"},
        {"title": "Azerbaijan", "value": "AZ"},
        {"title": "Bahrain", "value": "BH"},
        {"title": "Bangladesh", "value": "BD"},
        {"title": "Belgium", "value": "BE"},
        {"title": "Benin", "value": "BJ"},
        {"title": "Bhutan", "value": "BT"},
        {"title": "Bolivia, Plurinational State of", "value": "BO"},
        {"title": "Bosnia and Herzegovina", "value": "BA"},
        {"title": "Brunei Darussalam", "value": "BN"},
        {"title": "Bulgaria", "value": "BG"},
        {"title": "Canada", "value": "CA"},
        {"title": "Chile", "value": "CL"},
        {"title": "Colombia", "value": "CO"},
        {"title": "Costa Rica", "value": "CR"},
        {"title": "Croatia", "value": "HR"},
        {"title": "Cyprus", "value": "CY"},
        {"title": "Czechia", "value": "CZ"},
        {"title": "Côte d'Ivoire", "value": "CI"},
        {"title": "Denmark", "value": "DK"},
        {"title": "Dominican Republic", "value": "DO"},
        {"title": "Ecuador", "value": "EC"},
        {"title": "Egypt", "value": "EG"},
        {"title": "El Salvador", "value": "SV"},
        {"title": "Estonia", "value": "EE"},
        {"title": "Finland", "value": "FI"},
        {"title": "France", "value": "FR"},
        {"title": "Gambia", "value": "GM"},
        {"title": "Germany", "value": "DE"},
        {"title": "Ghana", "value": "GH"},
        {"title": "Greece", "value": "GR"},
        {"title": "Guatemala", "value": "GT"},
        {"title": "Guyana", "value": "GY"},
        {"title": "Hong Kong", "value": "HK"},
        {"title": "Hungary", "value": "HU"},
        {"title": "Iceland", "value": "IS"},
        {"title": "Indonesia", "value": "ID"},
        {"title": "Ireland", "value": "IE"},
        {"title": "Israel", "value": "IL"},
        {"title": "Italy", "value": "IT"},
        {"title": "Jamaica", "value": "JM"},
        {"title": "Japan", "value": "JP"},
        {"title": "Kenya", "value": "KE"},
        {"title": "Korea, Republic of", "value": "KR"},
        {"title": "Kuwait", "value": "KW"},
        {"title": "Latvia", "value": "LV"},
        {"title": "Liechtenstein", "value": "LI"},
        {"title": "Lithuania", "value": "LT"},
        {"title": "Luxembourg", "value": "LU"},
        {"title": "Malaysia", "value": "MY"},
        {"title": "Malta", "value": "MT"},
        {"title": "Mauritius", "value": "MU"},
        {"title": "Mexico", "value": "MX"},
        {"title": "Moldova, Republic of", "value": "MD"},
        {"title": "Monaco", "value": "MC"},
        {"title": "Morocco", "value": "MA"},
        {"title": "Namibia", "value": "NA"},
        {"title": "Netherlands", "value": "NL"},
        {"title": "New Zealand", "value": "NZ"},
        {"title": "Niger", "value": "NE"},
        {"title": "North Macedonia", "value": "MK"},
        {"title": "Norway", "value": "NO"},
        {"title": "Oman", "value": "OM"},
        {"title": "Panama", "value": "PA"},
        {"title": "Paraguay", "value": "PY"},
        {"title": "Peru", "value": "PE"},
        {"title": "Philippines", "value": "PH"},
        {"title": "Poland", "value": "PL"},
        {"title": "Portugal", "value": "PT"},
        {"title": "Qatar", "value": "QA"},
        {"title": "Romania", "value": "RO"},
        {"title": "Saint Lucia", "value": "LC"},
        {"title": "San Marino", "value": "SM"},
        {"title": "Saudi Arabia", "value": "SA"},
        {"title": "Senegal", "value": "SN"},
        {"title": "Serbia", "value": "RS"},
        {"title": "Singapore", "value": "SG"},
        {"title": "Slovakia", "value": "SK"},
        {"title": "Slovenia", "value": "SI"},
        {"title": "South Africa", "value": "ZA"},
        {"title": "Spain", "value": "ES"},
        {"title": "Sweden", "value": "SE"},
        {"title": "Switzerland", "value": "CH"},
        {"title": "Thailand", "value": "TH"},
        {"title": "Trinidad and Tobago", "value": "TT"},
        {"title": "Tunisia", "value": "TN"},
        {"title": "Türkiye", "value": "TR"},
        {"title": "United Arab Emirates", "value": "AE"},
        {"title": "United Kingdom", "value": "GB"},
        {"title": "United States", "value": "US"},
        {"title": "Uruguay", "value": "UY"},
    ],
}


def base_charge_succeeded_event():
    return {
        "id": "evt_test",
        "object": "event",
        "api_version": "2019-12-03",
        "created": 1617653203,
        "type": "charge.succeeded",
        "data": {
            "object": {
                "id": "ch_test",
                "object": "charge",
                "amount": 1500,
                "amount_captured": 1500,
                "amount_refunded": 0,
                "application": None,
                "application_fee": None,
                "application_fee_amount": None,
                "balance_transaction": "txn_test_balance",
                "billing_details": {
                    "address": {
                        "city": None,
                        "country": None,
                        "line1": None,
                        "line2": None,
                        "postal_code": None,
                        "state": None,
                    },
                    "email": None,
                    "name": None,
                    "phone": None,
                },
                "calculated_statement_descriptor": "ARTCONOMY.COM",
                "captured": True,
                "created": 1617653202,
                "currency": "usd",
                "customer": None,
                "description": "(created by Stripe CLI)",
                "destination": None,
                "dispute": None,
                "disputed": False,
                "failure_code": None,
                "failure_message": None,
                "fraud_details": {},
                "invoice": None,
                "livemode": False,
                "metadata": {},
                "on_behalf_of": None,
                "order": None,
                "outcome": {
                    "network_status": "approved_by_network",
                    "reason": None,
                    "risk_level": "normal",
                    "risk_score": 51,
                    "seller_message": "Payment complete.",
                    "type": "authorized",
                },
                "paid": True,
                "payment_intent": "pi_test",
                "payment_method": "card_test",
                "payment_method_details": {
                    "card": {
                        "brand": "visa",
                        "checks": {
                            "address_line1_check": None,
                            "address_postal_code_check": None,
                            "cvc_check": None,
                        },
                        "country": "US",
                        "exp_month": 4,
                        "exp_year": 2022,
                        "fingerprint": "UpCjmErZWs5fGhh7",
                        "funding": "credit",
                        "installments": None,
                        "last4": "4242",
                        "network": "visa",
                        "three_d_secure": None,
                        "wallet": None,
                    },
                    "type": "card",
                },
                "receipt_email": None,
                "receipt_number": None,
                "receipt_url": "https://pay.stripe.com/receipts/acct_1Fu0KSAhlvPza3BK/"
                "ch_test/"
                "rcpt_test",
                "refunded": False,
                "refunds": {
                    "object": "list",
                    "data": [],
                    "has_more": False,
                    "total_count": 0,
                    "url": "/v1/charges/ch_test/refunds",
                },
                "review": None,
                "shipping": None,
                "source": {
                    "id": "card_test",
                    "object": "card",
                    "address_city": None,
                    "address_country": None,
                    "address_line1": None,
                    "address_line1_check": None,
                    "address_line2": None,
                    "address_state": None,
                    "address_zip": None,
                    "address_zip_check": None,
                    "brand": "Visa",
                    "country": "US",
                    "customer": None,
                    "cvc_check": None,
                    "dynamic_last4": None,
                    "exp_month": 4,
                    "exp_year": 2022,
                    "fingerprint": "UpCjmErZWs5fGhh7",
                    "funding": "credit",
                    "last4": "4242",
                    "metadata": {},
                    "name": None,
                    "tokenization_method": None,
                },
                "source_transfer": None,
                "statement_descriptor": None,
                "statement_descriptor_suffix": None,
                "status": "succeeded",
                "transfer_data": None,
                "transfer_group": None,
            }
        },
        "livemode": False,
        "pending_webhooks": 1,
        "request": {"id": "req_test", "idempotency_key": None},
    }


def base_payment_method_attached_event():
    return {
        "id": "evt_1Icyh5AhlvPza3BKV9A13pSj",
        "object": "event",
        "api_version": "2019-12-03",
        "created": 1617653203,
        "type": "payment_method.attached",
        "data": {
            "object": {
                "id": "pm_w3eo4i7ugm34nner8ig",
                "object": "payment_method",
                "billing_details": {
                    "address": {
                        "city": None,
                        "country": None,
                        "line1": None,
                        "line2": None,
                        "postal_code": "77339",
                        "state": None,
                    },
                    "email": None,
                    "name": None,
                    "phone": None,
                },
                "card": {
                    "brand": "mastercard",
                    "checks": {
                        "address_line1_check": None,
                        "address_postal_code_check": "unchecked",
                        "cvc_check": "unchecked",
                    },
                    "country": "US",
                    "exp_month": 6,
                    "exp_year": 2024,
                    "fingerprint": "liuwmeq4gow234g",
                    "funding": "debit",
                    "generated_from": None,
                    "last4": "1111",
                    "networks": {"available": ["visa"], "preferred": None},
                    "three_d_secure_usage": {"supported": True},
                    "wallet": None,
                },
                "created": 1665407986,
                "customer": "cus_werogunser",
                "livemode": True,
                "metadata": {},
                "type": "card",
            }
        },
    }


def base_account_updated_event():
    return {
        "id": "evt_1Icyh5AhlvPza3BKV9A13pSj",
        "object": "event",
        "api_version": "2019-12-03",
        "created": 1617653203,
        "type": "account.updated",
        "data": {
            "object": {
                "id": "acct_slvew4334g9oj",
                "object": "account",
                "business_profile": {
                    "mcc": None,
                    "name": None,
                    "support_address": None,
                    "support_email": None,
                    "support_phone": None,
                    "support_url": None,
                    "url": "https://linjiang.pb.design/",
                },
                "capabilities": {"transfers": "active"},
                "charges_enabled": True,
                "country": "US",
                "created": 1666097221,
                "default_currency": "usd",
                "details_submitted": True,
                "email": "asdfsoim@example.com",
                "external_accounts": {
                    "object": "list",
                    "data": [
                        {
                            "id": "ba_asdpvo,werpob",
                            "object": "bank_account",
                            "account": "acct_slvew4334g9oj",
                            "account_holder_name": None,
                            "account_holder_type": None,
                            "account_type": None,
                            "available_payout_methods": ["standard"],
                            "bank_name": "BEEP BOOP BANK",
                            "country": "US",
                            "currency": "usd",
                            "default_for_currency": True,
                            "fingerprint": "Asiumf3e89w73e",
                            "last4": "1111",
                            "metadata": {},
                            "routing_number": "93457234",
                            "status": "new",
                        }
                    ],
                    "has_more": False,
                    "total_count": 1,
                    "url": "/v1/accounts/acct_slvew4334g9oj/external_accounts",
                },
                "future_requirements": {
                    "alternatives": [],
                    "current_deadline": None,
                    "currently_due": [],
                    "disabled_reason": None,
                    "errors": [],
                    "eventually_due": [],
                    "past_due": [],
                    "pending_verification": [],
                },
                "login_links": {
                    "object": "list",
                    "data": [],
                    "has_more": False,
                    "total_count": 0,
                    "url": "/v1/accounts/acct_slvew4334g9oj/login_links",
                },
                "metadata": {},
                "payouts_enabled": True,
                "requirements": {
                    "alternatives": [],
                    "current_deadline": None,
                    "currently_due": [],
                    "disabled_reason": None,
                    "errors": [],
                    "eventually_due": [],
                    "past_due": [],
                    "pending_verification": [],
                },
                "settings": {
                    "bacs_debit_payments": {},
                    "branding": {
                        "icon": None,
                        "logo": None,
                        "primary_color": None,
                        "secondary_color": None,
                    },
                    "card_issuing": {"tos_acceptance": {"date": None, "ip": None}},
                    "card_payments": {
                        "decline_on": {"avs_failure": False, "cvc_failure": False},
                        "statement_descriptor_prefix": None,
                        "statement_descriptor_prefix_kana": None,
                        "statement_descriptor_prefix_kanji": None,
                    },
                    "dashboard": {
                        "display_name": "beep.boop.design",
                        "timezone": "Etc/UTC",
                    },
                    "payments": {
                        "statement_descriptor": "BEEP.BOOP.DESIGN",
                        "statement_descriptor_kana": None,
                        "statement_descriptor_kanji": None,
                    },
                    "payouts": {
                        "debit_negative_balances": True,
                        "schedule": {"delay_days": 2, "interval": "daily"},
                        "statement_descriptor": None,
                    },
                    "sepa_debit_payments": {},
                },
                "tos_acceptance": {"date": 1666098001},
                "type": "express",
            },
            "previous_attributes": {
                "capabilities": {"transfers": "inactive"},
                "charges_enabled": False,
                "details_submitted": False,
                "payouts_enabled": False,
                "requirements": {
                    "currently_due": ["tos_acceptance.date", "tos_acceptance.ip"],
                    "disabled_reason": "requirements.past_due",
                    "eventually_due": ["tos_acceptance.date", "tos_acceptance.ip"],
                    "past_due": ["tos_acceptance.date", "tos_acceptance.ip"],
                },
                "tos_acceptance": {"date": None},
            },
        },
    }


def base_report_event():
    return {
        "id": "evt_1Icyh5AhlvPza3BKV9A13pSj",
        "object": "event",
        "api_version": "2019-12-03",
        "created": 1617653203,
        "type": "reporting.report_run.succeeded",
        "data": {
            "object": {
                "id": "frr_sdfbi7un4",
                "object": "reporting.report_run",
                "created": 1743188400,
                "error": None,
                "livemode": False,
                "parameters": {
                    "columns": [
                        "balance_transaction_id",
                        "created_utc",
                        "available_on_utc",
                        "reporting_category",
                        "gross",
                        "currency",
                        "description",
                    ],
                    "interval_end": 1743163200,
                    "interval_start": 1743015600,
                },
                "report_type": "balance_change_from_activity.itemized.3",
                "result": {
                    "id": "file_xdfgbkujnesrg",
                    "object": "file",
                    "created": 1743188434,
                    "expires_at": 1774724434,
                    "filename": "frr_sdfbi7un4.csv",
                    "links": {
                        "object": "list",
                        "data": [],
                        "has_more": False,
                        "url": "/v1/file_links?file=file_xdfgbkujnesrg",
                    },
                    "purpose": "finance_report_run",
                    "size": 1093,
                    "title": "FinanceReportRun frr_sdfbi7un4",
                    "type": "csv",
                    "url": "https://files.stripe.com/v1/files/file_xdfgbkujnesrg/contents",
                },
                "status": "succeeded",
                "succeeded_at": 1743188434,
            },
            "previous_attributes": None,
        },
    }


DUMMY_BALANCE_REPORT = """balance_transaction_id,created_utc,available_on_utc,reporting_category,gross,currency,description
txn_beep,2025-03-27 09:01:06,2025-03-27 09:01:06,fee,-0.08,usd,Radar (2025-03-26): Radar for Fraud Teams
txn_boop,2025-03-27 11:34:37,2025-03-27 11:34:37,transfer,-113.25,usd,
txn_foo,2025-03-27 19:09:17,2025-03-31 00:00:00,charge,80,usd,
txn_bar,2025-03-27 20:56:49,2025-03-28 21:00:00,transfer,-37.34,usd,
txn_wat,2025-03-27 23:11:51,2025-03-29 00:00:00,transfer,-71.15,usd,
txn_do,2025-03-27 23:12:01,2025-03-31 00:00:00,charge,7.65,usd,
txn_fox,2025-03-27 23:12:04,2025-03-31 00:00:00,transfer,-6.76,usd,
txn_vix,2025-03-28 05:00:01,2025-04-01 00:00:00,charge,9,usd,
txn_stuff,2025-03-28 09:18:43,2025-03-28 09:18:43,fee,-5.50,usd,Connect (2025-03-27): Cross-Border Transfers
txn_topup,2025-04-10 12:00:05,2025-04-10 12:00:05,topup,100,usd
"""
