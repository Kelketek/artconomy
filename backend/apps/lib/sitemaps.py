# Sitemap inclusion for the blog-generated sitemap.
import requests
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.utils import timezone
from bs4 import BeautifulSoup


def get_entries(url, cache):
    if cache.get("last_fetch") and cache.get("last_fetch") > (
        timezone.now() - relativedelta(weeks=1)
    ):
        return cache["locs"]
    data = requests.get(url)
    # Note: The lxml parser is potentially vulnerable to XML attacks. So these URLs
    # should only ever be trusted ones. If we need to start accepting untrusted
    # urls, we'll need to use defusedxml.
    soup = BeautifulSoup(
        data.content,
        features="xml",
    )
    cache["last_fetch"] = timezone.now()
    cache["locs"] = [
        {"lastmod": parse(url.lastmod.text), "location": url.loc.text}
        for url in soup.find_all("url")
    ]
    return cache["locs"]


def gen_sitemap_class(url):
    cache = {}

    class RemoteSitemap(Sitemap):
        def items(self):
            return get_entries(url, cache)

        def lastmod(self, item):
            return item["lastmod"]

        def location(self, item):
            return item["location"]

    return RemoteSitemap


maps = {
    label: gen_sitemap_class(url) for label, url in settings.EXTERNAL_SITEMAPS.items()
}
