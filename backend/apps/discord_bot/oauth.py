from authlib.integrations.django_client import OAuth
from django.conf import settings


oauth = OAuth()
oauth.register(
    'discord',
    client_id=settings.DISCORD_CLIENT_KEY,
    client_secret=settings.DISCORD_CLIENT_SECRET,
    authorize_url='https://discord.com/oauth2/authorize',
    authorize_params=None,
    access_token_url='https://discord.com/api/oauth2/token',
    access_token_params=None,
    api_base_url='https://discord.com/api',
    client_kwargs={
        'scope': 'guilds.join identify',
    },
)

discord_api = oauth.create_client('discord')
