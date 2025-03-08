import bs4
import html2text
from django.conf import settings


def make_url(base_url, overrides=None):
    overrides = overrides or {}
    context = {
        "proto": settings.DEFAULT_PROTOCOL,
        "domain": settings.DEFAULT_DOMAIN,
        **overrides,
    }
    if base_url.startswith("http"):
        return base_url
    return "{proto}://{domain}{base_url}".format(
        base_url=base_url,
        **context,
    )


def disable_on_load(signal_handler):
    def wrapper(*args, **kwargs):
        if kwargs.get("raw"):
            return
        signal_handler(*args, **kwargs)

    return wrapper


_textifier = html2text.HTML2Text()
_textifier.ignore_links = False
_textifier.reference_links = True
_textifier.body_width = float("inf")

invalid_tags = (("table", "div"), ("td", "span"), ("tr", "div"))


def strip_tags(html):
    soup = bs4.BeautifulSoup(html, features="lxml")
    for original, replacement in invalid_tags:
        for tag in soup.findAll(original):
            tag.name = replacement
    for link in soup.findAll("a"):
        if not link.text.strip():
            link.decompose()
            continue
        link.string = f"{link.text}: {link['href']}"
        link.name = "span"
    return soup


class Textifier:
    parser = _textifier

    def handle(self, html):
        soup = strip_tags(html)
        return self.parser.handle(str(soup))


def gen_textifier():
    return Textifier()
