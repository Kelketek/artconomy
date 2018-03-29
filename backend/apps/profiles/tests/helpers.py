from io import BytesIO

from PIL import Image
from avatar.templatetags.avatar_tags import avatar_url

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


def gen_image(**params):
    width = params.get('width', 100)
    height = params.get('height', width)
    color = params.get('color', 'blue')
    image_format = params.get('format', 'JPEG')

    thumb = Image.new('RGB', (width, height), color)
    thumb_io = BytesIO()
    thumb.save(thumb_io, format=image_format)
    return thumb_io.getvalue()
