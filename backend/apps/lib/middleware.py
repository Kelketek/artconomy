import re
from threading import currentThread

from dateutil import parser
from hitcount.utils import get_ip
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ResizablePagination(PageNumberPagination):
    page_size_query_param = "size"
    max_page_size = 50

    def get_paginated_response(self, data):
        return Response(
            {
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "count": self.page.paginator.count,
                "results": data,
                "size": self.get_page_size(self.request),
            }
        )


class OlderThanPagination(ResizablePagination):
    """
    Paginates a queryset based on when items in the set were created.
    """

    timestamp_query = "created_on__lt"

    def paginate_queryset(self, queryset, request, view=None):
        page_size = self.get_page_size(request)
        if not page_size:
            return None
        timestamp = request.GET.get("created_on", None)
        if not timestamp:
            return super().paginate_queryset(queryset, request, view=view)
        try:
            timestamp = parser.parse(timestamp)
        except ValueError:
            return super().paginate_queryset(queryset, request, view=view)
        return super().paginate_queryset(
            queryset.filter(**{self.timestamp_query: timestamp}), request, view=view
        )


ip_pattern = re.compile("[0-9]+[.][0-9]+[.][0-9]+[.][0-9]+")


class IPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get(
            "HTTP_CF_CONNECTING_IP", request.META.get("REMOTE_ADDR")
        ).strip()
        if ip_pattern.match(ip):
            request.ip4 = ip
            request.ip6 = None
        else:
            request.ip4 = None
            request.ip6 = ip
        request.ip = ip
        return self.get_response(request)


# Monkey patch the hitcount detector
def patched_get_ip(request):
    if not (request.ip4 or request.ip6):
        return get_ip(request)
    return request.ip4 or request.ip6


class MonkeyPatchMiddleWare:
    def __init__(self, get_response):
        from hitcount import views as hitcount_views

        hitcount_views.get_ip = patched_get_ip
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)


_requests = {}


def get_request():
    return _requests.get(currentThread(), None)


class GlobalRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _requests[currentThread()] = request
        response = self.get_response(request)
        _requests.pop(currentThread())
        return response

path_re = re.compile(r"/api/([^/]+)([/]v1[/])")


class VersionShimMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.path = path_re.sub(r"/api/\1/", request.path)
        request.path_info = request.path
        return self.get_response(request)
