from django.conf import settings
from pycountry import countries, subdivisions


def countries_tweaked():
    """
    Tweaked listing of countries.
    """
    us = countries.get(alpha_2='US')
    yield (us.alpha_2, us.name)
    for a in countries:
        if a.alpha_2 == 'TW':
            yield (a.alpha_2, "Taiwan")
        elif a.alpha_2 in settings.COUNTRIES_NOT_SERVED:
            continue
        elif a.alpha_2 != 'US':
            yield (a.alpha_2, a.name)


def country_choices():
    return [country_choice for country_choice in countries_tweaked()]


# Force pycountry to fetch data.
subdivisions.get(country_code='US')

subdivision_map = {
    country.alpha_2:
        {subdivision.code[3:]: subdivision.name for subdivision in subdivisions.get(country_code=country.alpha_2)}
        if country.alpha_2 in subdivisions.indices['country_code']
        else {}
    for country in countries
}

country_map = {country.name.lower(): country for country in countries}

for code, name in ('AE', 'AA', 'AP'):
    subdivision_map['US'][code] = code
