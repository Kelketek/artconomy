from django.conf import settings
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


def index(request):
    if request.method != 'GET':
        return bad_endpoint(request)
    if request.content_type == 'application/json':
        return bad_endpoint(request)
    return render(request, 'index.html', {'debug': settings.DEBUG})


@api_view(('GET', 'POST', 'PATCH', 'PUT', 'HEAD', 'DELETE', 'OPTIONS'))
def bad_endpoint(request):
    return Response(
        status=status.HTTP_404_NOT_FOUND, data={'error': '{} is not a valid API Endpoint.'.format(request.path)}
    )


def force_error_email(request):
    return 1 / 0
