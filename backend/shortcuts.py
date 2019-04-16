from django.conf import settings


def make_url(base_url):
    return "{proto}://{domain}{base_url}".format(
        proto=settings.DEFAULT_PROTOCOL,
        domain=settings.DEFAULT_DOMAIN,
        base_url=base_url,
    )


def disable_on_load(signal_handler):
    def wrapper(*args, **kwargs):
        if kwargs.get('raw'):
            return
        signal_handler(*args, **kwargs)
    return wrapper
