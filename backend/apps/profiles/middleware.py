from datetime import date

from apps.lib.abstract_models import ADULT, EXTREME, GENERAL, MATURE
from apps.lib.utils import check_theocratic_ban
from apps.profiles.models import User
from django.shortcuts import get_object_or_404


def derive_session_settings(*, user, session, ip):
    rating = GENERAL
    blacklist = []
    nsfw_blacklist = []
    session_settings = {}
    theocratic_ban = check_theocratic_ban(ip)
    if user.is_registered:
        sfw_mode = user.sfw_mode
        birthday = user.birthday
        verified_adult = user.verified_adult
        if not sfw_mode:
            rating = user.rating
            blacklist = user.blacklist.all()
            nsfw_blacklist = user.nsfw_blacklist.all()
    else:
        rating = session.get("rating", GENERAL)
        if rating not in [GENERAL, MATURE, ADULT, EXTREME]:
            rating = GENERAL
        sfw_mode = session.get("sfw_mode", False)
        birthday = session.get("birthday", None)
        verified_adult = False
        if birthday is not None:
            try:
                birthday = date.fromisoformat(birthday)
            except ValueError:
                birthday = None
    capped_rating = sfw_mode or (theocratic_ban and not verified_adult)
    session_settings["sfw_mode"] = sfw_mode
    session_settings["rating"] = rating
    session_settings["birthday"] = birthday
    session_settings["max_rating"] = GENERAL if capped_rating else rating
    session_settings["blacklist"] = blacklist
    session_settings["nsfw_blacklist"] = nsfw_blacklist
    session_settings["verified_adult"] = verified_adult
    session_settings["theocratic_ban"] = theocratic_ban
    return session_settings


class RatingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        session_settings = derive_session_settings(
            user=request.user,
            session=request.session,
            ip=request.ip,
        )
        # Annotate the session object with the session settings.
        for key, value in session_settings.items():
            setattr(request, key, value)
        return self.get_response(request)


class SubjectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def process_view(self, request, view_func, view_args, view_kwargs):
        if "username" in view_kwargs:
            request.subject = get_object_or_404(User, username=view_kwargs["username"])
