from apps.lib.abstract_models import GENERAL


def rating_middleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        rating = GENERAL
        blacklist= []
        if request.user.is_authenticated:
            if not request.user.sfw_mode:
                rating = request.user.rating
                blacklist = request.user.blacklist.all()
        request.max_rating = rating
        request.blacklist = blacklist

        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware
