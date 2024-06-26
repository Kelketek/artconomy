# Generated by Django 4.2.11 on 2024-04-09 21:18

from django.db import migrations


def update_positions(apps, schema):
    Submission = apps.get_model("profiles", "Submission")
    ArtistTag = apps.get_model("profiles", "ArtistTag")
    CharacterTag = apps.get_model("profiles", "CharacterTag")
    current = 0
    for submission in Submission.objects.all().order_by("display_position"):
        submission.display_position = current
        current += 1
        submission.save(update_fields=["display_position"])
    current = 0
    for tag in ArtistTag.objects.all().order_by("display_position"):
        tag.display_position = current
        current += 1
        tag.save(update_fields=["display_position"])
    current = 0
    for character in CharacterTag.objects.all().order_by("display_position"):
        character.display_position = current
        current += 1
        character.save(update_fields=["display_position"])


class Migration(migrations.Migration):

    dependencies = [
        ("profiles", "0140_add_verified_adult"),
    ]

    operations = [
        migrations.RunPython(update_positions, reverse_code=lambda x, y: None)
    ]
