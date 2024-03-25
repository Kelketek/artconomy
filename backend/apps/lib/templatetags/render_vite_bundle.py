# Yanked from: https://gist.github.com/lucianoratamero/7fc9737d24229ea9219f0987272896a2
# This template tag is needed for production. We have it because django_vite appears broken
# in our production use case, and it's not clear why.

import json
from itertools import chain

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


def markup_from_entry(entry: dict) -> str:
    file_name = entry['file']
    string = ""
    if file_name.lower().endswith('.js'):
        string += f"""<script type="module" src="/static/dist/{entry['file']}" crossOrigin="anonymous" async></script>"""
    elif file_name.lower().endswith('.css'):
        string += f"""<link rel="stylesheet" type="text/css" href="/static/dist/{entry['file']}" crossOrigin="anonymous"/>"""
    if "css" in entry:
        string += f"""<link rel="stylesheet" type="text/css" href="/static/dist/{entry['css'][0]}" crossOrigin="anonymous"/>"""
    return string


def embed_markup_from_entry(entry: dict) -> str:
    file_name = entry["file"]
    string = ""
    with open(f"{settings.VITE_APP_DIR}/dist/{file_name}") as file_handle:
        data = file_handle.read()
    if file_name.lower().endswith(".css"):
        string += f"<style>{data}</style>"
    elif file_name.lower().endswith(".js"):
        string += f"<script>{data}</script>"
    if "css" in entry:
        string += f"<style>{data}</style>"
    return string


def asset_markup(manifest: dict, file_name: str, inline: bool = False) -> str:
    if file_name.startswith("_"):
        # This is a derived asset name and may be in several pieces.
        entries = [
            manifest[key] for key in manifest.keys() if key.startswith(file_name)
        ]
    else:
        entries = [manifest[file_name]]
    transformer = embed_markup_from_entry if inline else markup_from_entry
    return "".join(transformer(entry) for entry in entries)


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
        "".join(
            chain(
                (
                    asset_markup(manifest, preload)
                    for preload in settings.PRELOADED_BUNDLE_ASSETS
                ),
                (
                    asset_markup(manifest, inline, inline=True)
                    for inline in settings.INLINE_BUNDLE_ASSETS
                ),
            ),
        )
    )
