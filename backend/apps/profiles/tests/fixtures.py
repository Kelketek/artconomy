from apps.profiles.social_matchers import SocialLinkSpec

LINK_TO_SOCIAL_SCENARIOS: tuple[tuple[str, SocialLinkSpec], ...] = (
    (
        "https://facebook.com/jimmy",
        {
            "site_name": "Facebook",
            "url": "https://www.facebook.com/jimmy/",
            "identifier": "jimmy",
        },
    ),
    (
        "https://www.facebook.com/jimmy/",
        {
            "site_name": "Facebook",
            "url": "https://www.facebook.com/jimmy/",
            "identifier": "jimmy",
        },
    ),
    (
        "https://www.instagram.com/artconomycom/",
        {
            "site_name": "Instagram",
            "url": "https://www.instagram.com/artconomycom/",
            "identifier": "artconomycom",
        },
    ),
    (
        "https://WEASYL.com/~booper",
        {
            "site_name": "Weasyl",
            "url": "https://weasyl.com/~booper",
            "identifier": "booper",
        },
    ),
    (
        "https://m.wEaSYL.com/profile/booper",
        {
            "site_name": "Weasyl",
            "url": "https://weasyl.com/~booper",
            "identifier": "booper",
        },
    ),
    (
        "https://toyhou.se/beep",
        {
            "site_name": "ToyHou.se",
            "url": "https://toyhou.se/beep",
            "identifier": "beep",
        },
    ),
    (
        "https://bsky.app/profile/vulpesveritas.bsky.social",
        {
            "site_name": "BlueSky",
            "url": "https://bsky.app/profile/vulpesveritas.bsky.social",
            "identifier": "vulpesveritas",
        },
    ),
    (
        "https://dork.carrd.co",
        {
            "site_name": "Carrd",
            "url": "https://dork.carrd.co/",
            "identifier": "",
        },
    ),
    (
        "https://twitter.com/Vulpes_Veritas",
        {
            "url": "https://x.com/Vulpes_Veritas",
            "site_name": "X",
            "identifier": "Vulpes_Veritas",
        },
    ),
    (
        "https://yiff.life/@VulpesVeritas",
        {
            "url": "https://yiff.life/@VulpesVeritas",
            "site_name": "yiff.life",
            "identifier": "VulpesVeritas",
        },
    ),
    (
        "https://dorkworld.com/profile/Herp",
        {
            "url": "https://dorkworld.com/profile/Herp",
            "site_name": "dorkworld.com",
            "identifier": "Herp",
        },
    ),
    (
        "https://www.deviantart.com/Blorp/about/",
        {
            "url": "https://www.deviantart.com/Blorp/",
            "site_name": "DeviantArt",
            "identifier": "Blorp",
        },
    ),
    (
        "https://example.com/",
        {
            "url": "https://example.com/",
            "site_name": "Website",
            "identifier": "",
        },
    ),
)
