from io import BytesIO

from apps.profiles.tests.factories import CharacterFactory, SubmissionFactory
from PIL import Image


def gen_characters(user, count=5, submission_count=3):
    characters = {}
    for index in range(count):
        character = CharacterFactory.create(user=user)
        characters[character] = []
        for i_index in range(submission_count):
            submission = SubmissionFactory.create(owner=user)
            submission.characters.add(character)
            if i_index == 0:
                character.primary_submission = submission
                character.save()
            characters[character].append(submission)
    return characters


def gen_image(**params):
    width = params.get("width", 100)
    height = params.get("height", width)
    color = params.get("color", "blue")
    image_format = params.get("format", "JPEG")

    thumb = Image.new("RGB", (width, height), color)
    thumb_io = BytesIO()
    thumb.save(thumb_io, format=image_format)
    return thumb_io.getvalue()
