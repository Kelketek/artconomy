# Yanked from: https://gist.github.com/lucianoratamero/7fc9737d24229ea9219f0987272896a2
# This template tag is needed for production. We have it because django_vite appears broken
# in our production use case, and it's not clear why.

import json

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def render_vite_bundle():
    """
    Template tag to render a vite bundle.
    Supposed to only be used in production.
    For development, see other files.
    """

    try:
        fd = open(f"{settings.VITE_APP_DIR}/dist/manifest.json", "r")
        manifest = json.load(fd)
    except:
        raise Exception(
            f"Vite manifest file not found or invalid. Maybe your {settings.VITE_APP_DIR}/dist/manifest.json file is empty?"
        )

    return mark_safe(
        f"""<script type="module" src="/static/dist/{manifest['index.html']['file']}" async></script>
        <link rel="stylesheet" type="text/css" href="/static/dist/{manifest['index.html']['css'][0]}"/>
"""
    )
