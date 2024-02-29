from git import Repo
from pathlib import Path

from django.contrib.sitemaps import Sitemap

repo = Repo(Path(__file__).parent / "..")
last_update = repo.head.reference.commit.authored_datetime

static_entries = (
    "/legal-and-policies/",
    "/legal-and-policies/refund-policy/",
    "/legal-and-policies/privacy-policy/",
    "/legal-and-policies/terms-of-service/",
    "/legal-and-policies/commission-agreement/",
    # Doesn't fill out with anything specific when visited, unlike other searches.
    "/search/profiles/",
)


class StaticSitemap(Sitemap):
    protocol = "https"
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return static_entries


high_dynamic_entries = (
    "/",
    "/session/settings/",
    "/search/products/",
    "/search/characters/",
    "/search/submissions/",
)


class HighDynamicSitemap(Sitemap):
    protocol = "https"
    changefreq = "hourly"
    priority = 1

    def items(self):
        return high_dynamic_entries

    def lastmod(self, item):
        return last_update

    def location(self, item):
        return item


# These items should be synced with the frontend views for the FAQ.
about_entries = ("what-is-artconomy", "cost", "team", "source-code")

buy_and_sell = (
    "how-to-buy",
    "how-to-sell",
    "shield",
    "disputes",
    "compare-and-contrast-plans",
    "landscape",
    "fee-calculation",
    "virtual-table",
    "bank-accounts",
    "workload-management",
    "outside-orders",
    "waitlists",
    "why-commissions-disabled",
    "paypal",
    "patreon-comparison",
    "featured-products",
    "security",
    "payouts",
    "crypto-currencies",
    "auctions",
    "physical-goods",
    "digital-downloads",
)

other = (
    "content-ratings",
    "content-policy",
    "tagging",
    "tag-blocking",
    "watching",
    "blocking",
    "file-formats",
)


class AboutSitemap(Sitemap):
    protocol = "https"
    priority = 1

    def items(self):
        return about_entries

    def lastmod(self, _):
        return last_update

    def location(self, item):
        return f"/faq/about/{item}/"


class BuyAndSellSitemap(Sitemap):
    protocol = "https"
    priority = 1

    def items(self):
        return buy_and_sell

    def lastmod(self, _):
        return last_update

    def location(self, item):
        return f"/faq/buying-and-selling/{item}/"


class OtherSitemap(Sitemap):
    protocol = "https"
    priority = 1

    def items(self):
        return other

    def lastmod(self, _):
        return last_update

    def location(self, item):
        return f"/faq/other/{item}/"
