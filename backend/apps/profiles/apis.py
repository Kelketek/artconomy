import dwollav2
from authorize import AuthorizeClient
from django.conf import settings
from rest_framework.reverse import reverse

from shortcuts import make_url

client = dwollav2.Client(
    key=settings.DWOLLA_KEY,
    secret=settings.DWOLLA_SECRET,
    environment='sandbox'
)

dwolla_api = client.Auth.client()


def dwolla_setup_link():
    return (
        "https://{mode}.dwolla.com/oauth/v2/authenticate?"
        "client_id={client_id}"
        "&response_type=code"
        "&redirect_uri={redirect_uri}"
        "&scope=Transactions"
        "&dwolla_landing=register"
    ).format(
        mode="sandbox" if settings.SANDBOX_APIS else "www",
        client_id=client.id,
        redirect_uri=make_url(reverse('profiles:register_dwolla')),
    )
