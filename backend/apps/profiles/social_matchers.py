"""
Functions for matching social media links to their accounts.
"""

from typing import TypedDict, Callable, cast
from urllib.parse import urlparse, ParseResult


class SocialLinkSpec(TypedDict):
    site_name: str
    url: str
    identifier: str


def fallback(parsed_url: ParseResult) -> SocialLinkSpec:
    """
    For when nothing matches, and nothing can be inferred.
    """
    return {
        "site_name": "Website",
        "url": parsed_url.geturl(),
        "identifier": "",
    }


def truncate_path(path: str) -> str:
    """
    Finds anything after the ? or # in a string and removes it.
    """
    string = path.split("?")[0]
    string = string.split("#")[0]
    return string


def build_default(parsed_url: ParseResult) -> SocialLinkSpec:
    """
    Builds a generic social link spec from a parsed URL.
    """
    identifier = ""
    site_name = "Website"
    common_style = False
    if parsed_url.path.startswith("/@"):
        identifier = parsed_url.path.split("/")[1][1:]
        common_style = True
    if parsed_url.path.startswith("/profile/"):
        identifier = parsed_url.path.replace("/profile/", "", 1)
        identifier = identifier.split("/")[0]
        common_style = True
    if common_style:
        site_name = parsed_url.hostname or "Website"
        # Not sure why the above doesn't cast correctly for my IDE, so casting here.
        site_name = cast(str, site_name)
        if site_name.startswith("www."):
            site_name = site_name.replace("www.", "", 1)
    if common_style:
        return {
            "site_name": site_name,
            "url": parsed_url.geturl(),
            "identifier": truncate_path(identifier),
        }
    return fallback(parsed_url)


def normalized_direct(
    canonical_root: str,
    site_name: str,
    parsed_url: ParseResult,
    trailing_slash=False,
) -> SocialLinkSpec:
    """
    Common profile URL format: https://example.com/username/
    """
    segments = parsed_url.path.split("/")
    try:
        username = segments[1]
    except IndexError:
        return build_default(parsed_url)
    suffix = ""
    if trailing_slash:
        suffix = "/"
    return {
        "site_name": site_name,
        "url": f"{canonical_root}/{username}" + suffix,
        "identifier": truncate_path(username),
    }


def facebook_parse(parsed_url: ParseResult) -> SocialLinkSpec:
    """Parse a Facebook link."""
    return normalized_direct(
        "https://www.facebook.com", "Facebook", parsed_url, trailing_slash=True
    )


def twitter_parse(parsed_url: ParseResult) -> SocialLinkSpec:
    """Parse a Twitter link."""
    return normalized_direct("https://x.com", "X", parsed_url)


def instagram_parse(parsed_url: ParseResult) -> SocialLinkSpec:
    """Parse an instagram link."""
    return normalized_direct(
        "https://www.instagram.com", "Instagram", parsed_url, trailing_slash=True
    )


def deviantart_parse(parsed_url: ParseResult) -> SocialLinkSpec:
    """Parse a DeviantArt link."""
    return normalized_direct(
        "https://www.deviantart.com", "DeviantArt", parsed_url, trailing_slash=True
    )


def toyhouse_parse(parsed_url: ParseResult) -> SocialLinkSpec:
    """Parse a toyhou.se link."""
    return normalized_direct("https://toyhou.se", "ToyHou.se", parsed_url)


def bsky_parse(parsed_url: ParseResult) -> SocialLinkSpec:
    """Parse a BlueSky link (for the main server)"""
    segments = parsed_url.path.split("/")
    try:
        identifier = truncate_path(segments[2]).removesuffix(".bsky.social")
    except IndexError:
        return fallback(parsed_url)
    return {
        "site_name": "BlueSky",
        "identifier": identifier,
        "url": f"https://bsky.app/profile/{identifier}.bsky.social",
    }


def weasyl_parse(parsed_url: ParseResult) -> SocialLinkSpec:
    """Parse a weasyl Link"""
    # Weasyl allows both /profile/ and ~/
    path = parsed_url.path.replace("/profile/", "/~", 1)
    if not path.startswith("/~"):
        return fallback(parsed_url)
    identifier = truncate_path(path.split("/")[1][1:])
    return {
        "site_name": "Weasyl",
        "url": f"https://weasyl.com/~{identifier}",
        "identifier": identifier,
    }


def carrd_parse(parsed_url: ParseResult) -> SocialLinkSpec:
    """Parse a carrd.co link."""
    return {
        "site_name": "Carrd",
        "url": f"https://{parsed_url.hostname}/",
        "identifier": "",
    }


KNOWN_SITES: dict[str, Callable[[ParseResult], SocialLinkSpec]] = {
    "facebook.com": facebook_parse,
    "instagram.com": instagram_parse,
    "twitter.com": twitter_parse,
    "x.com": twitter_parse,
    "carrd.co": carrd_parse,
    "bsky.app": bsky_parse,
    "weasyl.com": weasyl_parse,
    "deviantart.com": deviantart_parse,
    "toyhou.se": toyhouse_parse,
}


def link_to_social(link: str) -> SocialLinkSpec:
    """
    Given a URL string (validate beforehand), attempt to derive the SocialLinkSpec from
    the URL.
    """
    parsed_url = urlparse(link)
    hostname_segments = parsed_url.hostname.split(".")
    # Most sites have some subdomains that can vary-- a www or non-www version, or else
    # the subdomain itself is the username, such as with carrd.co.
    while len(hostname_segments) >= 2:
        hostname = ".".join(hostname_segments)
        result = KNOWN_SITES.get(hostname.lower(), lambda x: None)(parsed_url)
        if result:
            return result
        hostname_segments = hostname_segments[1:]

    return build_default(parsed_url)
