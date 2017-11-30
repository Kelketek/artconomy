from io import BytesIO

from PIL import Image

from apps.profiles.tests.factories import CharacterFactory, ImageAssetFactory


def gen_characters(user, count=5, asset_count=3):
    characters = {}
    for index in range(count):
        character = CharacterFactory.create(user=user)
        characters[character] = []
        for i_index in range(asset_count):
            asset = ImageAssetFactory.create(uploaded_by=user)
            asset.characters.add(character)
            if i_index == 0:
                character.primary_asset = asset
                character.save()
            characters[character].append(asset)
    return characters


def serialize_char(key, value):
    return {
        'id': key.id,
        'name': key.name,
        'description': key.description,
        'primary_asset': {
            'id': key.primary_asset.id,
            'file': 'http://testserver' + key.primary_asset.file.url,
            'title': key.primary_asset.title,
            'caption': key.primary_asset.caption,
            'private': key.primary_asset.private,
            'rating': key.primary_asset.rating,
            'created_on': key.primary_asset.created_on.isoformat().replace('+00:00', 'Z'),
            'uploaded_by': key.user.username
        },
        'private': key.private,
        'open_requests': key.open_requests,
        'open_requests_restrictions': key.open_requests_restrictions,
        'user': {
            'username': key.user.username,
            'id': key.user.id
        },
        'assets': [
            {
                'id': asset.id,
                'file': 'http://testserver' + asset.file.url,
                'title': asset.title,
                'caption': asset.caption,
                'private': asset.private,
                'rating': asset.rating,
                'created_on': asset.created_on.isoformat().replace('+00:00', 'Z'),
                'uploaded_by': key.user.username
            } for asset in value
        ]
    }


def gen_image(**params):
    width = params.get('width', 100)
    height = params.get('height', width)
    color = params.get('color', 'blue')
    image_format = params.get('format', 'JPEG')

    thumb = Image.new('RGB', (width, height), color)
    thumb_io = BytesIO()
    thumb.save(thumb_io, format=image_format)
    return thumb_io.getvalue()
