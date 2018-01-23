from django.db import connection
from django.db.models import Case, When, F, IntegerField, Q
from django.utils.text import slugify

from apps.profiles.models import Character, ImageAsset


def char_ordering(qs, requester):
    return qs.annotate(
        # Make target user characters negative so they're always first.
        mine=Case(
            When(user_id=requester.id, then=0-F('id')),
            default=F('id'),
            output_field=IntegerField(),
        )
    ).order_by('mine')


def available_chars(requester, query='', commissions=False, ordering=True):
    exclude = Q(private=True)
    if commissions:
        exclude |= Q(open_requests=False)
    qs = Character.objects.filter(
        name__istartswith=query
    ).exclude(exclude & ~Q(user=requester))

    if ordering:
        qs = char_ordering(qs, requester)
    return qs


def available_assets(request, requester):
    exclude = Q(private=True)
    if request.user.is_authenticated():
        exclude &= ~Q(uploaded_by=requester)
    return ImageAsset.objects.exclude(exclude).exclude(rating__gt=request.max_rating)


def tag_list_cleaner(tag_list):
    tag_list = [slugify(str(tag).lower().replace(' ', '')).replace('-', '_')[:50] for tag in tag_list]
    return list({tag for tag in tag_list if tag})


def ensure_tags(tag_list):
    if not tag_list:
        return
    with connection.cursor() as cursor:
        # Bulk get or create
        # Django's query prepper automatically wraps our arrays in parens, but we need to have them
        # act as individual values, so we have to custom build our placeholders here.
        statement = """
                    INSERT INTO profiles_tag (name)
                    (
                             SELECT i.name
                             FROM (VALUES {}) AS i(name)
                             LEFT JOIN profiles_tag as existing
                                     ON (existing.name = i.name)
                             WHERE existing.name IS NULL
                    )
                    """.format(('%s, ' * len(tag_list)).rsplit(',', 1)[0])
        cursor.execute(statement, [*tuple((tag,) for tag in tag_list)])
