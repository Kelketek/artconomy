# Generated by Django 2.2.1 on 2019-07-10 18:08
from django.contrib.contenttypes.models import ContentType
from django.db import migrations
from django.db.models import Count, Q

COMMENT = 4
NEW_PM = 25


def set_sender_participant(apps, schema):
    Conversation = apps.get_model("profiles.Conversation")
    ConversationParticipant = apps.get_model("profiles.ConversationParticipant")
    Event = apps.get_model("lib.Event")
    Comment = apps.get_model("lib.Comment")
    content_type = ContentType.objects.get_for_model(Conversation)
    for conversation in Conversation.objects.all():
        if not conversation.sender_left and conversation.sender:
            ConversationParticipant.objects.get_or_create(
                user=conversation.sender, conversation=conversation
            )
        if not all([conversation.subject, conversation.body]):
            # Could happen if we're reversing and moving forward again, if somene deleted a comment in the interim.
            # In such a case, we have no data with which to build our first comment with, and we should continue on.
            continue
        subject = conversation.subject
        subject = subject.replace("(", "\\(")
        subject = subject.replace(")", "\\)")
        subject = f"[//Subject]: # ({subject})\n"
        text = "[//]: # (Migrated. Do not edit or remove these header lines.)\n"
        text += subject
        text += conversation.body
        comment = Comment.objects.create(
            content_type_id=content_type.id,
            object_id=conversation.id,
            text=text,
            user=conversation.sender,
        )
        Comment.objects.filter(id=comment.id).update(
            edited=conversation.edited,
            edited_on=conversation.edited_on,
            created_on=conversation.created_on,
        )
        # This won't automatically produce notifications. The notifications should be filled in on the next comment.
        events = Event.objects.filter(
            type=COMMENT, content_type_id=content_type.id, object_id=conversation.id
        )
        for event in events:
            if not event.data:
                event.data = {"comments": [], "subcomments": []}
            event.data["comments"] = event.data["comments"] + [comment.id]
            event.save()
    Event.objects.filter(type=NEW_PM).delete()


def unset_sender_participant(apps, schema):
    Event = apps.get_model("lib.Event")
    Conversation = apps.get_model("profiles.Conversation")
    Subscription = apps.get_model("lib.Subscription")
    Comment = apps.get_model("lib.Comment")
    content_type = ContentType.objects.get_for_model(Conversation)
    comment_content_type = ContentType.objects.get_for_model(Conversation)
    for conversation in Conversation.objects.all():
        source_comment = (
            Comment.objects.filter(
                text__startswith="[//]: # (Migrated.",
                deleted=False,
                content_type_id=content_type.id,
                object_id=conversation.id,
            )
            .order_by("created_on")
            .first()
        )
        if source_comment is None:
            # We have no idea who started this conversation. Pick at random, and leave the fields empty.
            # We should never have an empty conversation, so this should at least end up sane.
            conversation.sender = conversation.participants.all().first()
            if conversation.sender is None:
                conversation.delete()
                continue
            conversation.save()
            continue
        lines = source_comment.text.split("\n")
        conversation.body = "\n".join(lines[2:])
        try:
            subject = lines[1]
        except IndexError:
            subject = ""
        subject = subject.replace("[//Subject]: # (", "", 1)
        subject = subject.rsplit(")")[0]
        subject = subject.replace("\\(", "(")
        subject = subject.replace("\\)", ")")
        conversation.subject = subject
        conversation.sender_id = source_comment.user_id
        conversation.save()
        for event in Event.objects.filter(data__comments__contains=source_comment.id):
            event.data["comments"] = [
                comment_id
                for comment_id in event.data["comments"]
                if comment_id != source_comment.id
            ]
            if not any([event.data["comments"], event.data["subcomments"]]):
                event.delete()
        Subscription.objects.filter(
            object_id=source_comment.id, content_type_id=comment_content_type.id
        ).delete()
        source_comment.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0086_message_to_conversation"),
    ]

    operations = [
        migrations.RunPython(
            set_sender_participant, reverse_code=unset_sender_participant
        )
    ]
