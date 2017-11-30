import requests

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from django.conf import settings

from shortcuts import make_url


def register_dwolla(request):
    """
    Gets the return code from a Dwolla registration and applies it to a user.
    """
    if not request.user.is_authenticated:
        return HttpResponse(
            status=status.HTTP_403_FORBIDDEN, content="Please log in and then re-attempt to link your account."
        )
    code = request.GET.get('code', '')
    if not code:
        return Response(status=status.HTTP_400_BAD_REQUEST, data="Code not provided.")
    result = requests.post(
        'https://{}.dwolla.com/oauth/v2/token'.format('sandbox' if settings.SANDBOX_APIS else 'www'),
        json={
            'client_id': settings.DWOLLA_KEY,
            'client_secret': settings.DWOLLA_SECRET,
            'code': code,
            "grant_type": "authorization_code",
            "redirect_uri": make_url(reverse('accounts:register_dwolla')),
        }
    )
    result.raise_for_status()
    request.user.dwolla_url = result.json()['_links']['account']['href']
    request.user.save()
    return redirect('/profiles/{}/'.format(request.user.username))
