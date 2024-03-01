import base_sitemaps
from apps.lib import sitemaps as lib_sitemaps
from apps.profiles import sitemaps as profile_sitemaps
from apps.sales import sitemaps as sales_sitemaps

sitemaps = {
    "UserAbout": profile_sitemaps.UserAboutSitemap,
    "UserProductListing": profile_sitemaps.UserProductListingSitemap,
    "CharacterListing": profile_sitemaps.UserCharactersListingSitemap,
    "UserFavoritesListing": profile_sitemaps.UserFavoritesListingSitemap,
    "UserArtGallery": profile_sitemaps.UserArtGallerySitemap,
    "UserArtCollection": profile_sitemaps.UserArtCollectionSitemap,
    "UserWatching": profile_sitemaps.UserWatchingSitemap,
    "UserWatchers": profile_sitemaps.UserWatchersSitemap,
    "Ratings": profile_sitemaps.RatingsSitemap,
    "Submission": profile_sitemaps.SubmissionSitemap,
    "Character": profile_sitemaps.CharacterSitemap,
    "Journal": profile_sitemaps.JournalSitemap,
    "Product": sales_sitemaps.ProductSitemap,
    "Static": base_sitemaps.StaticSitemap,
    "HighDynamic": base_sitemaps.HighDynamicSitemap,
    "About": base_sitemaps.AboutSitemap,
    "Other": base_sitemaps.OtherSitemap,
    "BuyAndSell": base_sitemaps.BuyAndSellSitemap,
    **lib_sitemaps.maps,
}
