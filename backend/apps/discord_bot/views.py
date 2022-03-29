from django.shortcuts import redirect
from django.urls import reverse
from rest_framework.decorators import api_view, permission_classes

from apps.discord_bot.oauth import discord_api
from apps.profiles.permissions import IsRegistered
from shortcuts import make_url


# Create your views here.
@api_view(['GET'])
@permission_classes([IsRegistered])
def auth(request):
    return discord_api.authorize_redirect(request, make_url(reverse('discord_bot:config')))


@api_view(['GET'])
@permission_classes([IsRegistered])
def config(request):
    token = discord_api.authorize_access_token(request)
    resp = discord_api.get('/api/users/@me', token=token)
    resp.raise_for_status()
    request.user.discord_id = resp.json()['id']
    request.user.save(update_fields=['discord_id'])
    return redirect(make_url('/my/Settings'))
