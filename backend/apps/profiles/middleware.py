from datetime import date
from uuid import uuid4

from apps.lib.abstract_models import GENERAL, MATURE, ADULT, EXTREME
from apps.profiles.models import User
from django.shortcuts import get_object_or_404


def derive_session_settings(*, user, session):
    rating = GENERAL
    blacklist = []
    session_settings = {}
    if user.is_registered:
        sfw_mode = user.sfw_mode
        birthday = user.birthday
        if not sfw_mode:
            rating = user.rating
            blacklist = user.blacklist.all()
    else:
        rating = session.get('rating', GENERAL)
        if rating not in [GENERAL, MATURE, ADULT]:
            rating = GENERAL
        sfw_mode = session.get('sfw_mode', False)
        birthday = session.get('birthday', None)
        if birthday is not None:
            try:
                birthday = date.fromisoformat(birthday)
            except ValueError:
                birthday = None
    session_settings['sfw_mode'] = sfw_mode
    session_settings['rating'] = rating
    session_settings['birthday'] = birthday
    session_settings['max_rating'] = GENERAL if sfw_mode else rating
    session_settings['blacklist'] = blacklist
    return session_settings


class RatingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        session_settings = derive_session_settings(user=request.user, session=request.session)
        # Annotate the session object with the session settings.
        for (key, value) in session_settings.items():
            setattr(request, key, value)
        return self.get_response(request)


class SubjectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def process_view(self, request, view_func, view_args, view_kwargs):
        if 'username' in view_kwargs:
            request.subject = get_object_or_404(User, username__iexact=view_kwargs['username'])
