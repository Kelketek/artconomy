from django.conf import settings


def settings_context(*_args):
    return {'settings': settings}
