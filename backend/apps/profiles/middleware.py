from datetime import date

from apps.lib.abstract_models import GENERAL, MATURE, ADULT, EXTREME
from apps.profiles.models import User
from django.shortcuts import get_object_or_404


class RatingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        rating = GENERAL
        blacklist = []
        if request.user.is_registered:
            sfw_mode = request.user.sfw_mode
            birthday = request.user.birthday
            if not sfw_mode:
                rating = request.user.rating
                blacklist = request.user.blacklist.all()
        else:
            rating = request.session.get('rating', GENERAL)
            if rating not in [GENERAL, MATURE, ADULT]:
                rating = GENERAL
            sfw_mode = request.session.get('sfw_mode', False)
            birthday = request.session.get('birthday', None)
            if birthday is not None:
                try:
                    birthday = date.fromisoformat(birthday)
                except ValueError:
                    birthday = None
        request.sfw_mode = sfw_mode
        request.rating = rating
        request.birthday = birthday
        request.max_rating = GENERAL if sfw_mode else rating
        request.blacklist = blacklist

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response


class SubjectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def process_view(self, request, view_func, view_args, view_kwargs):
        if 'username' in view_kwargs:
            request.subject = get_object_or_404(User, username__iexact=view_kwargs['username'])
