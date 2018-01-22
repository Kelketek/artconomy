from authorize import AuthorizeClient
from django.conf import settings

sauce = AuthorizeClient(settings.AUTHORIZE_KEY, settings.AUTHORIZE_SECRET, debug=settings.SANDBOX_APIS)
