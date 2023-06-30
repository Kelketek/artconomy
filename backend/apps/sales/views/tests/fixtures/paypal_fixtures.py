def invoice_paid_event():
    return {
        "id": "WH-45011818H7513372C-92K93122RK854913A",
        "create_time": "2023-07-25T23:55:45.656Z",
        "resource_type": "invoices",
        "event_type": "INVOICING.INVOICE.PAID",
        "summary": "An invoice is paid, partially paid, or payment "
        "is made and is pending.",
        "resource": {
            "invoice": {
                "id": "INV2-26KH-MY9Q-USVG-4WZD",
                "status": "PAID",
                "detail": {
                    "currency_code": "USD",
                    "category_code": "SHIPPABLE",
                    "invoice_number": "55t4gCZ-RPCA",
                    "invoice_date": "2023-07-25",
                    "payment_term": {
                        "term_type": "DUE_ON_RECEIPT",
                        "due_date": "2023-07-25",
                    },
                    "viewed_by_recipient": False,
                    "group_draft": False,
                    "metadata": {
                        "create_time": "2023-07-25T23:53:37Z",
                        "last_update_time": "2023-07-25T23:55:31Z",
                        "first_sent_time": "2023-07-25T23:53:39Z",
                        "last_sent_time": "2023-07-25T23:53:39Z",
                        "created_by_flow": "REGULAR_SINGLE",
                        "recipient_view_url": "https://www.sandbox.paypal.com/"
                        "invoice/p/#26KHMY9QUSVG4WZD",
                        "invoicer_view_url": "https://www.sandbox.paypal.com/"
                        "invoice/details/INV2-26KH-MY9Q-USVG-4WZD",
                        "caller_type": "API_V2_INVOICE",
                        "spam_info": {},
                    },
                    "archived": False,
                },
                "invoicer": {},
                "primary_recipients": [
                    {"billing_info": {"email_address": "kelketek+test@gmail.com"}}
                ],
                "items": [
                    {
                        "id": "ITEM-2HC901790X7563635",
                        "name": "Order #15 [Main] - Test product",
                        "quantity": "1",
                        "unit_amount": {"currency_code": "USD", "value": "25.00"},
                        "unit_of_measure": "AMOUNT",
                    }
                ],
                "configuration": {
                    "tax_calculated_after_discount": False,
                    "tax_inclusive": False,
                    "allow_tip": True,
                    "template_id": "TEMP-161977153R626473H",
                },
                "amount": {
                    "breakdown": {
                        "item_total": {"currency_code": "USD", "value": "25.00"},
                        "discount": {
                            "invoice_discount": {
                                "amount": {"currency_code": "USD", "value": "0.00"}
                            },
                            "item_discount": {"currency_code": "USD", "value": "0.00"},
                        },
                        "tax_total": {"currency_code": "USD", "value": "0.00"},
                    },
                    "currency_code": "USD",
                    "value": "25.00",
                },
                "due_amount": {"currency_code": "USD", "value": "0.00"},
                "payments": {
                    "paid_amount": {"currency_code": "USD", "value": "25.00"},
                    "transactions": [
                        {
                            "type": "PAYPAL",
                            "payment_id": "8E2904407M872241P",
                            "transaction_type": "SALE",
                            "payment_date": "2023-07-25",
                            "method": "PAYPAL",
                            "amount": {"currency_code": "USD", "value": "25.00"},
                            "transaction_status": "SUCCESS",
                        }
                    ],
                },
                "links": [
                    {
                        "href": "https://api.sandbox.paypal.com/v2/invoicing/"
                        "invoices/INV2-26KH-MY9Q-USVG-4WZD",
                        "rel": "self",
                        "method": "GET",
                    }
                ],
                "unilateral": False,
            }
        },
        "status": "SUCCESS",
        "transmissions": [
            {
                "webhook_url": "https://art-dev.ngrok.io/api/sales/"
                "paypal-webhooks/8se_jrJ6Sl6A/",
                "http_status": 204,
                "reason_phrase": "HTTP/1.1 200 Connection established",
                "response_headers": {
                    "X-Frame-Options": "DENY",
                    "Referrer-Policy": "same-origin",
                    "Ngrok-Trace-Id": "55bbce3d3a4765647efc15e8e7282d0a",
                    "Server": "nginx/1.25.1",
                    "X-Content-Type-Options": "nosniff",
                    "Connection": "keep-alive",
                    "Vary": "Accept, Cookie",
                    "Cross-Origin-Opener-Policy": "same-origin",
                    "Date": "Wed, 26 Jul 2023 00:24:16 GMT",
                    "Allow": "POST, OPTIONS",
                },
                "transmission_id": "bcd47ac0-2b4a-11ee-91e2-870aebfd036d",
                "status": "SUCCESS",
                "timestamp": "2023-07-25T23:55:48Z",
            }
        ],
        "links": [
            {
                "href": "https://api.sandbox.paypal.com/v1/notifications/"
                "webhooks-events/WH-45011818H7513372C-92K93122RK854913A",
                "rel": "self",
                "method": "GET",
                "encType": "application/json",
            },
            {
                "href": "https://api.sandbox.paypal.com/v1/notifications/"
                "webhooks-events/WH-45011818H7513372C-92K93122RK854913A/resend",
                "rel": "resend",
                "method": "POST",
                "encType": "application/json",
            },
        ],
        "event_version": "1.0",
    }


def invoice_refunded_event():
    return {
        "id": "WH-7XS20205PU358935W-8LE288564C9744152",
        "create_time": "2023-07-26T00:26:45.680Z",
        "resource_type": "invoices",
        "event_type": "INVOICING.INVOICE.REFUNDED",
        "summary": "An invoice is refunded or partially refunded.",
        "resource": {
            "invoice": {
                "id": "INV2-26KH-MY9Q-USVG-4WZD",
                "status": "REFUNDED",
                "detail": {
                    "currency_code": "USD",
                    "category_code": "SHIPPABLE",
                    "invoice_number": "55t4gCZ-RPCA",
                    "invoice_date": "2023-07-25",
                    "payment_term": {
                        "term_type": "DUE_ON_RECEIPT",
                        "due_date": "2023-07-25",
                    },
                    "viewed_by_recipient": False,
                    "group_draft": False,
                    "metadata": {
                        "create_time": "2023-07-25T23:53:37Z",
                        "last_update_time": "2023-07-26T00:26:33Z",
                        "first_sent_time": "2023-07-25T23:53:39Z",
                        "last_sent_time": "2023-07-25T23:53:39Z",
                        "created_by_flow": "REGULAR_SINGLE",
                        "recipient_view_url": "https://www.sandbox.paypal.com/"
                        "invoice/p/#26KHMY9QUSVG4WZD",
                        "invoicer_view_url": "https://www.sandbox.paypal.com/"
                        "invoice/details/INV2-26KH-MY9Q-USVG-4WZD",
                        "caller_type": "API_V2_INVOICE",
                        "spam_info": {},
                    },
                    "archived": False,
                },
                "invoicer": {},
                "primary_recipients": [
                    {"billing_info": {"email_address": "kelketek+test@gmail.com"}}
                ],
                "items": [
                    {
                        "id": "ITEM-2HC901790X7563635",
                        "name": "Order #15 [Main] - Test product",
                        "quantity": "1",
                        "unit_amount": {"currency_code": "USD", "value": "25.00"},
                        "unit_of_measure": "AMOUNT",
                    }
                ],
                "configuration": {
                    "tax_calculated_after_discount": False,
                    "tax_inclusive": False,
                    "allow_tip": True,
                    "template_id": "TEMP-161977153R626473H",
                },
                "amount": {
                    "breakdown": {
                        "item_total": {"currency_code": "USD", "value": "25.00"},
                        "discount": {
                            "invoice_discount": {
                                "amount": {"currency_code": "USD", "value": "0.00"}
                            },
                            "item_discount": {"currency_code": "USD", "value": "0.00"},
                        },
                        "tax_total": {"currency_code": "USD", "value": "0.00"},
                    },
                    "currency_code": "USD",
                    "value": "25.00",
                },
                "due_amount": {"currency_code": "USD", "value": "0.00"},
                "payments": {
                    "paid_amount": {"currency_code": "USD", "value": "25.00"},
                    "transactions": [
                        {
                            "type": "PAYPAL",
                            "payment_id": "8E2904407M872241P",
                            "transaction_type": "SALE",
                            "payment_date": "2023-07-25",
                            "method": "PAYPAL",
                            "amount": {"currency_code": "USD", "value": "25.00"},
                            "transaction_status": "SUCCESS",
                        }
                    ],
                },
                "refunds": {
                    "refund_amount": {"currency_code": "USD", "value": "25.00"},
                    "transactions": [
                        {
                            "type": "PAYPAL",
                            "recipient_transaction_id": "17155493DW2108105",
                            "refund_date": "2023-07-25",
                            "amount": {"currency_code": "USD", "value": "25.00"},
                        }
                    ],
                },
                "links": [
                    {
                        "href": "https://api.sandbox.paypal.com/v2/invoicing/"
                        "invoices/INV2-26KH-MY9Q-USVG-4WZD",
                        "rel": "self",
                        "method": "GET",
                    }
                ],
                "unilateral": False,
            }
        },
        "status": "SUCCESS",
        "transmissions": [
            {
                "webhook_url": "https://art-dev.ngrok.io/api/sales/"
                "paypal-webhooks/8se_jrJ6Sl6A/",
                "http_status": 204,
                "reason_phrase": "HTTP/1.1 200 Connection established",
                "response_headers": {
                    "X-Frame-Options": "DENY",
                    "Referrer-Policy": "same-origin",
                    "Ngrok-Trace-Id": "94c47302955bdbb7283ae29cff2975cb",
                    "Server": "nginx/1.25.1",
                    "X-Content-Type-Options": "nosniff",
                    "Connection": "keep-alive",
                    "Vary": "Accept, Cookie",
                    "Cross-Origin-Opener-Policy": "same-origin",
                    "Date": "Wed, 26 Jul 2023 00:27:06 GMT",
                    "Allow": "POST, OPTIONS",
                },
                "transmission_id": "1edaa050-2b4b-11ee-91d9-77f873e6b262",
                "status": "SUCCESS",
                "timestamp": "2023-07-26T00:26:53Z",
            }
        ],
        "links": [
            {
                "href": "https://api.sandbox.paypal.com/v1/notifications/"
                "webhooks-events/WH-7XS20205PU358935W-8LE288564C9744152",
                "rel": "self",
                "method": "GET",
                "encType": "application/json",
            },
            {
                "href": "https://api.sandbox.paypal.com/v1/notifications/"
                "webhooks-events/WH-7XS20205PU358935W-8LE288564C9744152/resend",
                "rel": "resend",
                "method": "POST",
                "encType": "application/json",
            },
        ],
        "event_version": "1.0",
    }


def invoice_cancelled_event():
    return {
        "id": "WH-4M1994083W792541C-1JF12205NY372445E",
        "create_time": "2023-07-25T21:34:15.508Z",
        "resource_type": "invoices",
        "event_type": "INVOICING.INVOICE.CANCELLED",
        "summary": "A merchant or customer cancels an invoice.",
        "resource": {
            "invoice": {
                "id": "INV2-T8LF-A7N8-D7SA-NDSV",
                "status": "CANCELLED",
                "detail": {
                    "currency_code": "USD",
                    "category_code": "SHIPPABLE",
                    "invoice_number": "K_zlffz8QLqA",
                    "invoice_date": "2023-07-25",
                    "payment_term": {
                        "term_type": "DUE_ON_RECEIPT",
                        "due_date": "2023-07-25",
                    },
                    "viewed_by_recipient": False,
                    "group_draft": False,
                    "metadata": {
                        "create_time": "2023-07-25T21:22:42Z",
                        "last_update_time": "2023-07-25T21:22:43Z",
                        "cancel_time": "2023-07-25T21:34:01Z",
                        "first_sent_time": "2023-07-25T21:22:45Z",
                        "last_sent_time": "2023-07-25T21:22:45Z",
                        "created_by_flow": "REGULAR_SINGLE",
                        "recipient_view_url": "https://www.sandbox.paypal.com/"
                        "invoice/p/#T8LFA7N8D7SANDSV",
                        "invoicer_view_url": "https://www.sandbox.paypal.com/"
                        "invoice/details/INV2-T8LF-A7N8-D7SA-NDSV",
                        "caller_type": "API_V2_INVOICE",
                        "spam_info": {},
                    },
                    "archived": False,
                },
                "invoicer": {},
                "primary_recipients": [
                    {"billing_info": {"email_address": "kelketek+test@gmail.com"}}
                ],
                "items": [
                    {
                        "id": "ITEM-8L908173MC907843L",
                        "name": "Order #14 [Main] - Test product",
                        "quantity": "1",
                        "unit_amount": {"currency_code": "USD", "value": "25.00"},
                        "unit_of_measure": "AMOUNT",
                    }
                ],
                "configuration": {
                    "tax_calculated_after_discount": False,
                    "tax_inclusive": False,
                    "allow_tip": True,
                    "template_id": "TEMP-161977153R626473H",
                },
                "amount": {
                    "breakdown": {
                        "item_total": {"currency_code": "USD", "value": "25.00"},
                        "discount": {
                            "invoice_discount": {
                                "amount": {"currency_code": "USD", "value": "0.00"}
                            },
                            "item_discount": {"currency_code": "USD", "value": "0.00"},
                        },
                        "tax_total": {"currency_code": "USD", "value": "0.00"},
                    },
                    "currency_code": "USD",
                    "value": "25.00",
                },
                "due_amount": {"currency_code": "USD", "value": "25.00"},
                "links": [
                    {
                        "href": "https://api.sandbox.paypal.com/v2/invoicing/"
                        "invoices/INV2-T8LF-A7N8-D7SA-NDSV",
                        "rel": "self",
                        "method": "GET",
                    }
                ],
                "unilateral": False,
            }
        },
        "status": "SUCCESS",
        "transmissions": [
            {
                "webhook_url": "https://art-dev.ngrok.io/api/sales/"
                "paypal-webhooks/8se_jrJ6Sl6A/",
                "http_status": 204,
                "reason_phrase": "HTTP/1.1 200 Connection established",
                "response_headers": {
                    "X-Frame-Options": "DENY",
                    "Referrer-Policy": "same-origin",
                    "Ngrok-Trace-Id": "a517774c3a8ae65d187d9b18252d4cf0",
                    "Server": "nginx/1.25.1",
                    "X-Content-Type-Options": "nosniff",
                    "Connection": "keep-alive",
                    "Vary": "Accept, Cookie",
                    "Cross-Origin-Opener-Policy": "same-origin",
                    "Date": "Tue, 25 Jul 2023 21:51:52 GMT",
                    "Allow": "POST, OPTIONS",
                },
                "transmission_id": "05d70c50-2b33-11ee-91e2-870aebfd036d",
                "status": "SUCCESS",
                "timestamp": "2023-07-25T21:34:23Z",
            }
        ],
        "links": [
            {
                "href": "https://api.sandbox.paypal.com/v1/notifications/"
                "webhooks-events/WH-4M1994083W792541C-1JF12205NY372445E",
                "rel": "self",
                "method": "GET",
                "encType": "application/json",
            },
            {
                "href": "https://api.sandbox.paypal.com/v1/notifications/"
                "webhooks-events/WH-4M1994083W792541C-1JF12205NY372445E/resend",
                "rel": "resend",
                "method": "POST",
                "encType": "application/json",
            },
        ],
        "event_version": "1.0",
    }


def invoice_updated_event():
    return {
        "create_time": "2023-08-08T16:58:46.357Z",
        "event_type": "INVOICING.INVOICE.UPDATED",
        "event_version": "1.0",
        "id": "WH-7E484915859563401-03846870AX698884E",
        "links": [
            {
                "href": "https://api.sandbox.paypal.com/v1/notifications"
                "/webhooks-events/WH-7E484915859563401-03846870AX698884E",
                "method": "GET",
                "rel": "self",
            },
            {
                "href": "https://api.sandbox.paypal.com/v1/notifications"
                "/webhooks-events/WH-7E484915859563401-03846870AX698884E"
                "/resend",
                "method": "POST",
                "rel": "resend",
            },
        ],
        "resource": {
            "invoice": {
                "amount": {
                    "breakdown": {
                        "custom": {
                            "amount": {"currency_code": "USD", "value": "3.00"},
                            "label": "Beep",
                        },
                        "discount": {
                            "invoice_discount": {
                                "amount": {"currency_code": "USD", "value": "-5.00"}
                            },
                            "item_discount": {"currency_code": "USD", "value": "-5.00"},
                        },
                        "item_total": {"currency_code": "USD", "value": "100.00"},
                        "shipping": {
                            "amount": {"currency_code": "USD", "value": "10.00"}
                        },
                        "tax_total": {"currency_code": "USD", "value": "5.00"},
                    },
                    "currency_code": "USD",
                    "value": "108.00",
                },
                "configuration": {
                    "allow_tip": True,
                    "tax_calculated_after_discount": False,
                    "tax_inclusive": False,
                    "template_id": "TEMP-161977153R626473H",
                },
                "detail": {
                    "archived": False,
                    "category_code": "SHIPPABLE",
                    "currency_code": "USD",
                    "group_draft": False,
                    "invoice_date": "2023-08-08",
                    "invoice_number": "3AL51CYcS_mA",
                    "metadata": {
                        "caller_type": "API_V2_INVOICE",
                        "create_time": "2023-08-08T16:25:34Z",
                        "created_by_flow": "REGULAR_SINGLE",
                        "first_sent_time": "2023-08-08T16:25:36Z",
                        "invoicer_view_url": "https://www.sandbox.paypal.com/invoice"
                        "/details/INV2-EJ5S-JNXQ-X49P-JC3B",
                        "last_sent_time": "2023-08-08T16:25:36Z",
                        "last_update_time": "2023-08-08T16:58:31Z",
                        "recipient_view_url": "https://www.sandbox.paypal.com/invoice"
                        "/p/#EJ5SJNXQX49PJC3B",
                        "spam_info": {},
                    },
                    "payment_term": {
                        "due_date": "2023-08-08",
                        "term_type": "DUE_ON_RECEIPT",
                    },
                    "viewed_by_recipient": False,
                },
                "due_amount": {"currency_code": "USD", "value": "108.00"},
                "id": "INV2-EJ5S-JNXQ-X49P-JC3B",
                "invoicer": {},
                "items": [
                    {
                        "description": "Derpitude",
                        "discount": {
                            "amount": {"currency_code": "USD", "value": "-5.00"},
                            "percent": "5",
                        },
                        "id": "ITEM-9C187971WJ767573D",
                        "name": "Order #23 [Main] - Test product",
                        "quantity": "4",
                        "tax": {
                            "amount": {"currency_code": "USD", "value": "5.00"},
                            "id": "TAX-2EY16269UU309405U",
                            "name": "Dorkus",
                            "percent": "5",
                        },
                        "unit_amount": {"currency_code": "USD", "value": "25.00"},
                        "unit_of_measure": "HOURS",
                    }
                ],
                "links": [
                    {
                        "href": "https://api.sandbox.paypal.com/v2/invoicing"
                        "/invoices/INV2-EJ5S-JNXQ-X49P-JC3B",
                        "method": "GET",
                        "rel": "self",
                    },
                    {
                        "href": "https://api.sandbox.paypal.com/v2/invoicing"
                        "/invoices/INV2-EJ5S-JNXQ-X49P-JC3B",
                        "method": "PUT",
                        "rel": "replace",
                    },
                    {
                        "href": "https://api.sandbox.paypal.com/v2/invoicing"
                        "/invoices/INV2-EJ5S-JNXQ-X49P-JC3B/cancel",
                        "method": "POST",
                        "rel": "cancel",
                    },
                    {
                        "href": "https://api.sandbox.paypal.com/v2/invoicing"
                        "/invoices/INV2-EJ5S-JNXQ-X49P-JC3B/remind",
                        "method": "POST",
                        "rel": "remind",
                    },
                    {
                        "href": "https://api.sandbox.paypal.com/v2/invoicing"
                        "/invoices/INV2-EJ5S-JNXQ-X49P-JC3B/payments",
                        "method": "POST",
                        "rel": "record-payment",
                    },
                    {
                        "href": "https://api.sandbox.paypal.com/v2/invoicing"
                        "/invoices/INV2-EJ5S-JNXQ-X49P-JC3B/generate-qr-code",
                        "method": "GET",
                        "rel": "qr-code",
                    },
                ],
                "primary_recipients": [
                    {"billing_info": {"email_address": "kelketek+paypal@gmail.com"}}
                ],
                "status": "SENT",
                "unilateral": True,
            }
        },
        "resource_type": "invoices",
        "summary": "An invoice is updated.",
    }
