# Note: This constant and the one following it must be kept in sync,
# as they are the end-to-end result of a test.
def gen_stripe_countries_output():
    return {'default_currency': 'usd',
            'id': 'US',
            'object': 'country_spec',
            'supported_bank_account_currencies': {'usd': ['US']},
            'supported_payment_currencies': ['usd',
                                             'aed',
                                             'afn',
                                             'all',
                                             'amd',
                                             'ang',
                                             'aoa',
                                             'ars',
                                             'aud',
                                             'awg',
                                             'azn',
                                             'bam',
                                             'bbd',
                                             'bdt',
                                             'bgn',
                                             'bif',
                                             'bmd',
                                             'bnd',
                                             'bob',
                                             'brl',
                                             'bsd',
                                             'bwp',
                                             'byn',
                                             'bzd',
                                             'cad',
                                             'cdf',
                                             'chf',
                                             'clp',
                                             'cny',
                                             'cop',
                                             'crc',
                                             'cve',
                                             'czk',
                                             'djf',
                                             'dkk',
                                             'dop',
                                             'dzd',
                                             'egp',
                                             'etb',
                                             'eur',
                                             'fjd',
                                             'fkp',
                                             'gbp',
                                             'gel',
                                             'gip',
                                             'gmd',
                                             'gnf',
                                             'gtq',
                                             'gyd',
                                             'hkd',
                                             'hnl',
                                             'hrk',
                                             'htg',
                                             'huf',
                                             'idr',
                                             'ils',
                                             'inr',
                                             'isk',
                                             'jmd',
                                             'jpy',
                                             'kes',
                                             'kgs',
                                             'khr',
                                             'kmf',
                                             'krw',
                                             'kyd',
                                             'kzt',
                                             'lak',
                                             'lbp',
                                             'lkr',
                                             'lrd',
                                             'lsl',
                                             'mad',
                                             'mdl',
                                             'mga',
                                             'mkd',
                                             'mmk',
                                             'mnt',
                                             'mop',
                                             'mro',
                                             'mur',
                                             'mvr',
                                             'mwk',
                                             'mxn',
                                             'myr',
                                             'mzn',
                                             'nad',
                                             'ngn',
                                             'nio',
                                             'nok',
                                             'npr',
                                             'nzd',
                                             'pab',
                                             'pen',
                                             'pgk',
                                             'php',
                                             'pkr',
                                             'pln',
                                             'pyg',
                                             'qar',
                                             'ron',
                                             'rsd',
                                             'rub',
                                             'rwf',
                                             'sar',
                                             'sbd',
                                             'scr',
                                             'sek',
                                             'sgd',
                                             'shp',
                                             'sll',
                                             'sos',
                                             'srd',
                                             'std',
                                             'szl',
                                             'thb',
                                             'tjs',
                                             'top',
                                             'try',
                                             'ttd',
                                             'twd',
                                             'tzs',
                                             'uah',
                                             'ugx',
                                             'uyu',
                                             'uzs',
                                             'vnd',
                                             'vuv',
                                             'wst',
                                             'xaf',
                                             'xcd',
                                             'xof',
                                             'xpf',
                                             'yer',
                                             'zar',
                                             'zmw'],
            'supported_payment_methods': ['ach', 'card', 'stripe'],
            'supported_transfer_countries': ['US',
                                             'AE',
                                             'AR',
                                             'AT',
                                             'AU',
                                             'BE',
                                             'BG',
                                             'BO',
                                             'CA',
                                             'CH',
                                             'CI',
                                             'CL',
                                             'CO',
                                             'CR',
                                             'CY',
                                             'CZ',
                                             'DE',
                                             'DK',
                                             'DO',
                                             'EE',
                                             'EG',
                                             'ES',
                                             'FI',
                                             'FR',
                                             'GB',
                                             'GM',
                                             'GR',
                                             'HK',
                                             'HR',
                                             'HU',
                                             'ID',
                                             'IE',
                                             'IL',
                                             'IS',
                                             'IT',
                                             'JP',
                                             'KE',
                                             'KR',
                                             'LI',
                                             'LT',
                                             'LU',
                                             'LV',
                                             'MA',
                                             'MT',
                                             'MX',
                                             'MY',
                                             'NL',
                                             'NO',
                                             'NZ',
                                             'PE',
                                             'PH',
                                             'PL',
                                             'PT',
                                             'PY',
                                             'RO',
                                             'RS',
                                             'SA',
                                             'SE',
                                             'SG',
                                             'SI',
                                             'SK',
                                             'SV',
                                             'TH',
                                             'TN',
                                             'TR',
                                             'TT',
                                             'UY',
                                             'ZA',
                                             'BD',
                                             'BJ',
                                             'JM',
                                             'MC',
                                             'NE',
                                             'SN',
                                             'AG',
                                             'BH',
                                             'GH',
                                             'GT',
                                             'GY',
                                             'KW',
                                             'LC',
                                             'MU',
                                             'NA',
                                             'SM',
                                             'AM',
                                             'BA',
                                             'OM',
                                             'PA',
                                             'AZ',
                                             'BN',
                                             'BT',
                                             'EC',
                                             'MD',
                                             'MK',
                                             'QA'],
            'verification_fields': {'company': {'additional': [],
                                                'minimum': ['business_profile.mcc',
                                                            'business_profile.url',
                                                            'business_type',
                                                            'company.address.city',
                                                            'company.address.line1',
                                                            'company.address.postal_code',
                                                            'company.address.state',
                                                            'company.name',
                                                            'company.phone',
                                                            'company.tax_id',
                                                            'external_account',
                                                            'relationship.owner',
                                                            'relationship.representative',
                                                            'tos_acceptance.date',
                                                            'tos_acceptance.ip']},
                                    'individual': {'additional': [],
                                                   'minimum': ['business_profile.mcc',
                                                               'business_profile.url',
                                                               'business_type',
                                                               'external_account',
                                                               'individual.address.city',
                                                               'individual.address.line1',
                                                               'individual.address.postal_code',
                                                               'individual.address.state',
                                                               'individual.dob.day',
                                                               'individual.dob.month',
                                                               'individual.dob.year',
                                                               'individual.email',
                                                               'individual.first_name',
                                                               'individual.id_number',
                                                               'individual.last_name',
                                                               'individual.phone',
                                                               'individual.ssn_last_4',
                                                               'individual.verification.document',
                                                               'tos_acceptance.date',
                                                               'tos_acceptance.ip']}}}


COUNTRIES_ARTCONOMY_OUTPUT = {'countries': [{'text': 'Antigua and Barbuda', 'value': 'AG'},
                                            {'text': 'Argentina', 'value': 'AR'},
                                            {'text': 'Armenia', 'value': 'AM'},
                                            {'text': 'Australia', 'value': 'AU'},
                                            {'text': 'Austria', 'value': 'AT'},
                                            {'text': 'Azerbaijan', 'value': 'AZ'},
                                            {'text': 'Bahrain', 'value': 'BH'},
                                            {'text': 'Bangladesh', 'value': 'BD'},
                                            {'text': 'Belgium', 'value': 'BE'},
                                            {'text': 'Benin', 'value': 'BJ'},
                                            {'text': 'Bhutan', 'value': 'BT'},
                                            {'text': 'Bolivia, Plurinational State of', 'value': 'BO'},
                                            {'text': 'Bosnia and Herzegovina', 'value': 'BA'},
                                            {'text': 'Brunei Darussalam', 'value': 'BN'},
                                            {'text': 'Bulgaria', 'value': 'BG'},
                                            {'text': 'Canada', 'value': 'CA'},
                                            {'text': 'Chile', 'value': 'CL'},
                                            {'text': 'Colombia', 'value': 'CO'},
                                            {'text': 'Costa Rica', 'value': 'CR'},
                                            {'text': 'Croatia', 'value': 'HR'},
                                            {'text': 'Cyprus', 'value': 'CY'},
                                            {'text': 'Czechia', 'value': 'CZ'},
                                            {'text': "Côte d'Ivoire", 'value': 'CI'},
                                            {'text': 'Denmark', 'value': 'DK'},
                                            {'text': 'Dominican Republic', 'value': 'DO'},
                                            {'text': 'Ecuador', 'value': 'EC'},
                                            {'text': 'Egypt', 'value': 'EG'},
                                            {'text': 'El Salvador', 'value': 'SV'},
                                            {'text': 'Estonia', 'value': 'EE'},
                                            {'text': 'Finland', 'value': 'FI'},
                                            {'text': 'France', 'value': 'FR'},
                                            {'text': 'Gambia', 'value': 'GM'},
                                            {'text': 'Germany', 'value': 'DE'},
                                            {'text': 'Ghana', 'value': 'GH'},
                                            {'text': 'Greece', 'value': 'GR'},
                                            {'text': 'Guatemala', 'value': 'GT'},
                                            {'text': 'Guyana', 'value': 'GY'},
                                            {'text': 'Hong Kong', 'value': 'HK'},
                                            {'text': 'Hungary', 'value': 'HU'},
                                            {'text': 'Iceland', 'value': 'IS'},
                                            {'text': 'Indonesia', 'value': 'ID'},
                                            {'text': 'Ireland', 'value': 'IE'},
                                            {'text': 'Israel', 'value': 'IL'},
                                            {'text': 'Italy', 'value': 'IT'},
                                            {'text': 'Jamaica', 'value': 'JM'},
                                            {'text': 'Japan', 'value': 'JP'},
                                            {'text': 'Kenya', 'value': 'KE'},
                                            {'text': 'Korea, Republic of', 'value': 'KR'},
                                            {'text': 'Kuwait', 'value': 'KW'},
                                            {'text': 'Latvia', 'value': 'LV'},
                                            {'text': 'Liechtenstein', 'value': 'LI'},
                                            {'text': 'Lithuania', 'value': 'LT'},
                                            {'text': 'Luxembourg', 'value': 'LU'},
                                            {'text': 'Malaysia', 'value': 'MY'},
                                            {'text': 'Malta', 'value': 'MT'},
                                            {'text': 'Mauritius', 'value': 'MU'},
                                            {'text': 'Mexico', 'value': 'MX'},
                                            {'text': 'Moldova, Republic of', 'value': 'MD'},
                                            {'text': 'Monaco', 'value': 'MC'},
                                            {'text': 'Morocco', 'value': 'MA'},
                                            {'text': 'Namibia', 'value': 'NA'},
                                            {'text': 'Netherlands', 'value': 'NL'},
                                            {'text': 'New Zealand', 'value': 'NZ'},
                                            {'text': 'Niger', 'value': 'NE'},
                                            {'text': 'North Macedonia', 'value': 'MK'},
                                            {'text': 'Norway', 'value': 'NO'},
                                            {'text': 'Oman', 'value': 'OM'},
                                            {'text': 'Panama', 'value': 'PA'},
                                            {'text': 'Paraguay', 'value': 'PY'},
                                            {'text': 'Peru', 'value': 'PE'},
                                            {'text': 'Philippines', 'value': 'PH'},
                                            {'text': 'Poland', 'value': 'PL'},
                                            {'text': 'Portugal', 'value': 'PT'},
                                            {'text': 'Qatar', 'value': 'QA'},
                                            {'text': 'Romania', 'value': 'RO'},
                                            {'text': 'Saint Lucia', 'value': 'LC'},
                                            {'text': 'San Marino', 'value': 'SM'},
                                            {'text': 'Saudi Arabia', 'value': 'SA'},
                                            {'text': 'Senegal', 'value': 'SN'},
                                            {'text': 'Serbia', 'value': 'RS'},
                                            {'text': 'Singapore', 'value': 'SG'},
                                            {'text': 'Slovakia', 'value': 'SK'},
                                            {'text': 'Slovenia', 'value': 'SI'},
                                            {'text': 'South Africa', 'value': 'ZA'},
                                            {'text': 'Spain', 'value': 'ES'},
                                            {'text': 'Sweden', 'value': 'SE'},
                                            {'text': 'Switzerland', 'value': 'CH'},
                                            {'text': 'Thailand', 'value': 'TH'},
                                            {'text': 'Trinidad and Tobago', 'value': 'TT'},
                                            {'text': 'Tunisia', 'value': 'TN'},
                                            {'text': 'Turkey', 'value': 'TR'},
                                            {'text': 'United Arab Emirates', 'value': 'AE'},
                                            {'text': 'United Kingdom', 'value': 'GB'},
                                            {'text': 'United States', 'value': 'US'},
                                            {'text': 'Uruguay', 'value': 'UY'}]}


def base_charge_succeeded_event():
    return {
        'id': 'evt_1Icyh5AhlvPza3BKV9A13pSj',
        'object': 'event',
        'api_version': '2019-12-03',
        'created': 1617653203,
        'type': 'charge.succeeded',
        'data': {
            'object': {
                'id': 'ch_1Icyh4AhlvPza3BK7ZkPN95S',
                'object': 'charge',
                'amount': 1500,
                'amount_captured': 1500,
                'amount_refunded': 0,
                'application': None,
                'application_fee': None,
                'application_fee_amount': None,
                'balance_transaction': 'txn_1Icyh5AhlvPza3BKKv8oUs3e',
                'billing_details': {
                    'address': {
                        'city': None,
                        'country': None,
                        'line1': None,
                        'line2': None,
                        'postal_code': None,
                        'state': None
                    },
                    'email': None,
                    'name': None,
                    'phone': None
                },
                'calculated_statement_descriptor': 'ARTCONOMY.COM',
                'captured': True,
                'created': 1617653202,
                'currency': 'usd',
                'customer': None,
                'description': '(created by Stripe CLI)',
                'destination': None,
                'dispute': None,
                'disputed': False,
                'failure_code': None,
                'failure_message': None,
                'fraud_details': {},
                'invoice': None,
                'livemode': False,
                'metadata': {},
                'on_behalf_of': None,
                'order': None,
                'outcome': {
                    'network_status': 'approved_by_network',
                    'reason': None,
                    'risk_level': 'normal',
                    'risk_score': 51,
                    'seller_message': 'Payment complete.',
                    'type': 'authorized'
                },
                'paid': True,
                'payment_intent': 'pi_asrdfo8uyv7234',
                'payment_method': 'card_1Icyh4AhlvPza3BKKfHLWtEW',
                'payment_method_details': {
                    'card': {
                        'brand': 'visa',
                        'checks': {
                            'address_line1_check': None,
                            'address_postal_code_check': None,
                            'cvc_check': None
                        },
                        'country': 'US',
                        'exp_month': 4,
                        'exp_year': 2022,
                        'fingerprint': 'UpCjmErZWs5fGhh7',
                        'funding': 'credit',
                        'installments': None,
                        'last4': '4242',
                        'network': 'visa',
                        'three_d_secure': None,
                        'wallet': None
                    },
                    'type': 'card'
                },
                'receipt_email': None,
                'receipt_number': None,
                'receipt_url': 'https://pay.stripe.com/receipts/acct_1Fu0KSAhlvPza3BK/ch_1Icyh4AhlvPza3BK7ZkPN95S/rcpt_JFTe7703FypdF9BO3C6kfZcrouVJ2Wm',
                'refunded': False,
                'refunds': {
                    'object': 'list',
                    'data': [],
                    'has_more': False,
                    'total_count': 0,
                    'url': '/v1/charges/ch_1Icyh4AhlvPza3BK7ZkPN95S/refunds'
                },
                'review': None,
                'shipping': None,
                'source': {
                    'id': 'card_1Icyh4AhlvPza3BKKfHLWtEW',
                    'object': 'card',
                    'address_city': None,
                    'address_country': None,
                    'address_line1': None,
                    'address_line1_check': None,
                    'address_line2': None,
                    'address_state': None,
                    'address_zip': None,
                    'address_zip_check': None,
                    'brand': 'Visa',
                    'country': 'US',
                    'customer': None,
                    'cvc_check': None,
                    'dynamic_last4': None,
                    'exp_month': 4,
                    'exp_year': 2022,
                    'fingerprint': 'UpCjmErZWs5fGhh7',
                    'funding': 'credit',
                    'last4': '4242',
                    'metadata': {},
                    'name': None,
                    'tokenization_method': None
                },
                'source_transfer': None,
                'statement_descriptor': None,
                'statement_descriptor_suffix': None,
                'status': 'succeeded',
                'transfer_data': None,
                'transfer_group': None
            }
        },
        'livemode': False,
        'pending_webhooks': 1,
        'request': {
            'id': 'req_jcqQXmSfMGTwR2',
            'idempotency_key': None
        },
    }


def base_payment_method_attached_event():
    return {
        'id': 'evt_1Icyh5AhlvPza3BKV9A13pSj',
        'object': 'event',
        'api_version': '2019-12-03',
        'created': 1617653203,
        'type': 'payment_method.attached',
        'data': {
            'object': {
                'id': 'pm_w3eo4i7ugm34nner8ig',
                'object': 'payment_method',
                'billing_details': {
                    'address': {
                        'city': None,
                        'country': None,
                        'line1': None,
                        'line2': None,
                        'postal_code': '77339',
                        'state': None
                    },
                    'email': None,
                    'name': None,
                    'phone': None
                },
                'card': {
                    'brand': 'mastercard',
                    'checks': {
                        'address_line1_check': None,
                        'address_postal_code_check': 'unchecked',
                        'cvc_check': 'unchecked'
                    },
                    'country': 'US',
                    'exp_month': 6,
                    'exp_year': 2024,
                    'fingerprint': 'liuwmeq4gow234g',
                    'funding': 'debit',
                    'generated_from': None,
                    'last4': '1111',
                    'networks': {
                        'available': [
                            'visa'
                        ],
                        'preferred': None
                    },
                    'three_d_secure_usage': {
                        'supported': True
                    },
                    'wallet': None
                },
                'created': 1665407986,
                'customer': 'cus_werogunser',
                'livemode': True,
                'metadata': {
                },
                'type': 'card'
            }
        },
    }


def base_report_event():
    return {
        'id': 'evt_1Icyh5AhlvPza3BKV9A13pSj',
        'object': 'event',
        'api_version': '2019-12-03',
        'created': 1617653203,
        'type': 'reporting.report_run.succeeded',
        'data': {
            'object': {
                'id': 'frr_1LthdqAhlvPza3BKcoeR0Gxa',
                'object': 'reporting.report_run',
                'created': 1665968238,
                'error': None,
                'livemode': True,
                'parameters': {
                    'columns': [
                        'source_id',
                        'gross',
                        'net',
                        'fee',
                        'currency',
                        'automatic_payout_effective_at_utc'
                    ],
                    'connected_account': 'acct_asdfawselkm',
                    'payout': 'po_237uhawseivo2'
                },
                'report_type': 'connected_account_payout_reconciliation.by_id.itemized.4',
                'result': {
                    'id': 'file_as8e7fh2w3eun',
                    'object': 'file',
                    'created': 1665968255,
                    'expires_at': 1697504255,
                    'filename': 'frr_ascivunw8ieu7n2.csv',
                    'links': {
                        'object': 'list',
                        'data': [
                        ],
                        'has_more': False,
                        'url': '/v1/file_links?file=file_asdvwoeudmva'
                    },
                    'purpose': 'finance_report_run',
                    'size': 162,
                    'title': 'FinanceReportRun frr_1LthdqAhlvPza3BKcoeR0Gxa',
                    'type': 'csv',
                    'url': 'https://files.stripe.com/v1/files/file_asdvwoeudmva/contents'
                },
                'status': 'succeeded',
                'succeeded_at': 1665968255
            }
        },
    }


def base_account_updated_event():
    return {
        'id': 'evt_1Icyh5AhlvPza3BKV9A13pSj',
        'object': 'event',
        'api_version': '2019-12-03',
        'created': 1617653203,
        'type': 'account.updated',
        'data': {
            'object': {
                'id': 'acct_slvew4334g9oj',
                'object': 'account',
                'business_profile': {
                    'mcc': None,
                    'name': None,
                    'support_address': None,
                    'support_email': None,
                    'support_phone': None,
                    'support_url': None,
                    'url': 'https://linjiang.pb.design/'
                },
                'capabilities': {
                    'transfers': 'active'
                },
                'charges_enabled': True,
                'country': 'US',
                'created': 1666097221,
                'default_currency': 'usd',
                'details_submitted': True,
                'email': 'asdfsoim@example.com',
                'external_accounts': {
                    'object': 'list',
                    'data': [
                        {
                            'id': 'ba_asdpvo,werpob',
                            'object': 'bank_account',
                            'account': 'acct_slvew4334g9oj',
                            'account_holder_name': None,
                            'account_holder_type': None,
                            'account_type': None,
                            'available_payout_methods': [
                                'standard'
                            ],
                            'bank_name': 'BEEP BOOP BANK',
                            'country': 'US',
                            'currency': 'usd',
                            'default_for_currency': True,
                            'fingerprint': 'Asiumf3e89w73e',
                            'last4': '1111',
                            'metadata': {
                            },
                            'routing_number': '93457234',
                            'status': 'new'
                        }
                    ],
                    'has_more': False,
                    'total_count': 1,
                    'url': '/v1/accounts/acct_slvew4334g9oj/external_accounts'
                },
                'future_requirements': {
                    'alternatives': [
                    ],
                    'current_deadline': None,
                    'currently_due': [
                    ],
                    'disabled_reason': None,
                    'errors': [
                    ],
                    'eventually_due': [
                    ],
                    'past_due': [
                    ],
                    'pending_verification': [
                    ]
                },
                'login_links': {
                    'object': 'list',
                    'data': [
                    ],
                    'has_more': False,
                    'total_count': 0,
                    'url': '/v1/accounts/acct_slvew4334g9oj/login_links'
                },
                'metadata': {
                },
                'payouts_enabled': True,
                'requirements': {
                    'alternatives': [
                    ],
                    'current_deadline': None,
                    'currently_due': [
                    ],
                    'disabled_reason': None,
                    'errors': [
                    ],
                    'eventually_due': [
                    ],
                    'past_due': [
                    ],
                    'pending_verification': [
                    ]
                },
                'settings': {
                    'bacs_debit_payments': {
                    },
                    'branding': {
                        'icon': None,
                        'logo': None,
                        'primary_color': None,
                        'secondary_color': None
                    },
                    'card_issuing': {
                        'tos_acceptance': {
                            'date': None,
                            'ip': None
                        }
                    },
                    'card_payments': {
                        'decline_on': {
                            'avs_failure': False,
                            'cvc_failure': False
                        },
                        'statement_descriptor_prefix': None,
                        'statement_descriptor_prefix_kana': None,
                        'statement_descriptor_prefix_kanji': None
                    },
                    'dashboard': {
                        'display_name': 'beep.boop.design',
                        'timezone': 'Etc/UTC'
                    },
                    'payments': {
                        'statement_descriptor': 'BEEP.BOOP.DESIGN',
                        'statement_descriptor_kana': None,
                        'statement_descriptor_kanji': None
                    },
                    'payouts': {
                        'debit_negative_balances': True,
                        'schedule': {
                            'delay_days': 2,
                            'interval': 'daily'
                        },
                        'statement_descriptor': None
                    },
                    'sepa_debit_payments': {
                    }
                },
                'tos_acceptance': {
                    'date': 1666098001
                },
                'type': 'express'
            },
            'previous_attributes': {
                'capabilities': {
                    'transfers': 'inactive'
                },
                'charges_enabled': False,
                'details_submitted': False,
                'payouts_enabled': False,
                'requirements': {
                    'currently_due': [
                        'tos_acceptance.date',
                        'tos_acceptance.ip'
                    ],
                    'disabled_reason': 'requirements.past_due',
                    'eventually_due': [
                        'tos_acceptance.date',
                        'tos_acceptance.ip'
                    ],
                    'past_due': [
                        'tos_acceptance.date',
                        'tos_acceptance.ip'
                    ]
                },
                'tos_acceptance': {
                    'date': None
                }
            }
        }
    }


def base_payout_paid_event():
    return {
        'id': 'evt_asevo8iwm3e9v8',
        'object': 'event',
        'account': 'acct_wileu4mg3io',
        'api_version': '2019-12-03',
        'created': 1666051581,
        'type': 'payout.paid',
        'data': {
            'object': {
                'id': 'po_qwefoimwdv0wer',
                'object': 'payout',
                'amount': 4786,
                'arrival_date': 1666051200,
                'automatic': True,
                'balance_transaction': 'txn_des4rlgiumwegji',
                'created': 1665718571,
                'currency': 'gbp',
                'description': 'STRIPE PAYOUT',
                'destination': 'ba_1KslcPPTqmUQyuulPnZYDQWh',
                'failure_balance_transaction': None,
                'failure_code': None,
                'failure_message': None,
                'livemode': True,
                'metadata': {
                },
                'method': 'standard',
                'original_payout': None,
                'reversed_by': None,
                'source_type': 'card',
                'statement_descriptor': 'ARTCONOMY',
                'status': 'paid',
                'type': 'bank_account'
            }
        },
        'livemode': True,
        'pending_webhooks': 1,
        'request': {
            'id': None,
            'idempotency_key': None
        },
    }


DUMMY_REPORT = b"""source_id,gross,net,fee,currency,automatic_payout_effective_at_utc
py_xoser87gh23o8hwer,47.86,47.86,0,gbp,2022-10-01 00:00:00"""

DUMMY_REVERSE_REPORT = b"""source_id,gross,net,fee,currency,automatic_payout_effective_at_utc
pyr_xoser87gh23o8hwer,-47.86,-47.86,0,gbp,2022-10-01 00:00:00"""

DUMMY_REPORT_NO_EFFECTIVE_TIME = b"""source_id,gross,net,fee,currency,automatic_payout_effective_at_utc
py_xoser87gh23o8hwer,47.86,47.86,0,gbp,"""
