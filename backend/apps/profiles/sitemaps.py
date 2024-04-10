from django.contrib.sitemaps import Sitemap
from apps.profiles.models import User, Submission, Journal, Character


class UserAboutSitemap(Sitemap):
    priority = 0.7
    protocol = "https"

    def items(self):
        return User.objects.filter(is_active=True, guest=False)

    def lastmod(self, item):
        return item.last_login or item.date_joined

    def location(self, item):
        return f"/profile/{item.username}/about/"


class UserQueueSitemap(Sitemap):
    priority = 0.3
    protocol = "https"

    def items(self):
        return User.objects.filter(
            is_active=True,
            guest=False,
            artist_mode=True,
            artist_profile__public_queue=True,
        )

    def lastmod(self, item):
        order = item.sales.order_by("-created_on").first()
        if not order:
            return item.last_login or item.date_joined
        return order.created_on

    def location(self, item):
        return f"/profile/{item.username}/queue/"


class UserProductListingSitemap(Sitemap):
    priority = 0.6
    protocol = "https"

    def items(self):
        return User.objects.filter(is_active=True, guest=False, artist_mode=True)

    def lastmod(self, obj):
        product = (
            obj.products.filter(
                active=True,
                hidden=False,
            )
            .order_by("-edited_on")
            .first()
        )
        if not product:
            return obj.date_joined
        return product.edited_on

    def location(self, item):
        return f"/profile/{item.username}/products/"


class UserCharactersListingSitemap(Sitemap):
    protocol = "https"

    def items(self):
        return User.objects.filter(is_active=True, guest=False)

    def lastmod(self, obj):
        character = (
            obj.characters.filter(
                private=False,
            )
            .order_by("-created_on")
            .first()
        )
        if not character:
            return obj.date_joined
        return character.created_on

    def location(self, item):
        return f"/profile/{item.username}/characters/"


class UserFavoritesListingSitemap(Sitemap):
    priority = 0.4
    protocol = "https"

    def items(self):
        return User.objects.filter(is_active=True, guest=False, favorites_hidden=False)

    def lastmod(self, item):
        return item.last_login or item.date_joined

    def location(self, item):
        return f"/profile/{item.username}/favorites/"


class UserArtGallerySitemap(Sitemap):
    protocol = "https"

    def items(self):
        return User.objects.filter(is_active=True, guest=False)

    def lastmod(self, item):
        submission = item.art.order_by("-created_on").first()
        if not submission:
            return item.last_login or item.date_joined
        return submission.created_on

    def location(self, item):
        return f"/profile/{item.username}/gallery/art/"


class UserArtCollectionSitemap(Sitemap):
    protocol = "https"

    def items(self):
        return User.objects.filter(is_active=True, guest=False)

    def lastmod(self, item):
        submission = (
            item.owned_profiles_submission.exclude(artists=item)
            .order_by("-created_on")
            .first()
        )
        if not submission:
            return item.last_login or item.date_joined
        return submission.created_on

    def location(self, item):
        return f"/profile/{item.username}/gallery/collection/"


class UserWatchingSitemap(Sitemap):
    protocol = "https"
    priority = 0.3

    def items(self):
        return User.objects.filter(is_active=True, guest=False)

    def lastmod(self, item):
        return item.last_login or item.date_joined

    def location(self, item):
        return f"/profile/{item.username}/watchlists/watching/"


class UserWatchersSitemap(Sitemap):
    protocol = "https"
    priority = 0.3

    def items(self):
        return User.objects.filter(is_active=True, guest=False)

    def lastmod(self, item):
        return item.last_login or item.date_joined

    def location(self, item):
        return f"/profile/{item.username}/watchlists/watchers/"


class SubmissionSitemap(Sitemap):
    protocol = "https"

    def items(self):
        return Submission.objects.filter(private=False, owner__is_active=True)

    def lastmod(self, item):
        comment = item.comments.order_by("-created_on").first()
        if not comment:
            return item.created_on
        return comment.created_on

    def location(self, item):
        return f"/submissions/{item.id}/"


class CharacterSitemap(Sitemap):
    protocol = "https"

    def items(self):
        return Character.objects.filter(private=False, user__is_active=True)

    def lastmod(self, item):
        submission = item.submissions.order_by("-created_on").first()
        if not submission:
            return item.created_on
        return submission.created_on

    def location(self, item):
        return f"/profile/{item.user.username}/characters/{item.name}/"


class JournalSitemap(Sitemap):
    protocol = "https"
    priority = 0.3

    def items(self):
        return Journal.objects.filter(user__is_active=True)

    def lastmod(self, item):
        return item.created_on

    def location(self, item):
        return f"/profile/{item.user.username}/journals/{item.id}/"


class RatingsSitemap(Sitemap):
    priority = 0.2
    protocol = "https"

    def items(self):
        return User.objects.filter(is_active=True, guest=False).exclude(stars=None)

    def lastmod(self, item):
        rating = item.ratings_received.order_by("-created_on").first()
        if not rating:
            return item.last_login or item.date_joined

    def location(self, item):
        return f"/profile/{item.username}/ratings/"
