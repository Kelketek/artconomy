import re

from dateutil import parser
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ResizablePagination(PageNumberPagination):
    page_size_query_param = 'size'
    max_page_size = 50

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data,
            "size": self.get_page_size(self.request),
        })


class OlderThanPagination(ResizablePagination):
    """
    Paginates a queryset based on when items in the set were created.
    """

    timestamp_query = 'created_on__lt'

    def paginate_queryset(self, queryset, request, view=None):
        page_size = self.get_page_size(request)
        if not page_size:
            return None
        timestamp = request.GET.get('created_on', None)
        if not timestamp:
            return super().paginate_queryset(queryset, request, view=view)
        try:
            timestamp = parser.parse(timestamp)
        except ValueError:
            return super().paginate_queryset(queryset, request, view=view)
        return super().paginate_queryset(queryset.filter(**{self.timestamp_query: timestamp}), request, view=view)


ip_pattern = re.compile('[0-9]+[.][0-9]+[.][0-9]+[.][0-9]+')


class IPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip4 = request.META.get('HTTP_CF_CONNECTING_IP', request.META.get('REMOTE_ADDR')).strip()
        if ip_pattern.match(ip4):
            request.ip4 = ip4
        else:
            request.ip4 = None
        return self.get_response(request)
