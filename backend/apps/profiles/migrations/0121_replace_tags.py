# Generated by Django 3.2.13 on 2022-05-07 09:14

from django.db import migrations

from apps.profiles.models import get_next_artist_position, get_next_submission_position, get_next_character_position


def create_tags(apps, schema):
    ArtistTag = apps.get_model('profiles', 'ArtistTag')
    CharacterTag = apps.get_model('profiles', 'CharacterTag')
    Submission = apps.get_model('profiles', 'Submission')
    for tag in Submission.artists.through.objects.all().order_by('submission__created_on'):
        ArtistTag.objects.get_or_create(user=tag.user, submission=tag.submission, display_position=get_next_artist_position())
    for tag in Submission.characters.through.objects.all().order_by('submission__created_on'):
        CharacterTag.objects.get_or_create(character=tag.character, submission=tag.submission, display_position=get_next_character_position())
    for submission in Submission.objects.order_by('created_on'):
        submission.display_position = get_next_submission_position()
        submission.save()


def transpose_tags(apps, schema):
    ArtistTag = apps.get_model('profiles', 'ArtistTag')
    CharacterTag = apps.get_model('profiles', 'CharacterTag')
    for tag in ArtistTag.objects.all():
        tag.submission.artists.add(tag.user)
    for tag in CharacterTag.objects.all():
        tag.submission.characters.add(tag.character)


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0120_auto_20220507_0409'),
    ]

    operations = [
        migrations.RunPython(create_tags, reverse_code=transpose_tags)
    ]