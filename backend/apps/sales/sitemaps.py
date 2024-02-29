from django.contrib.sitemaps import Sitemap

from apps.sales.models import Product


class ProductSitemap(Sitemap):
    priority = 0.8
    protocol = "https"

    def items(self):
        return Product.objects.filter(
            hidden=False,
            user__is_active=True,
        )

    def lastmod(self, item):
        return item.edited_on

    def location(self, item):
        return f"/store/{item.user}/product/{item.id}/"
