from django.conf import settings


def make_url(base_url):
    return "{proto}://{domain}{base_url}".format(
        proto=settings.DEFAULT_PROTOCOL,
        domain=settings.DEFAULT_DOMAIN,
        base_url=base_url,
    )
