import os
import time
from pathlib import Path

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management import BaseCommand
from django.template.loader import get_template

from apps.profiles.models import User
from shortcuts import gen_textifier


class Command(BaseCommand):
    help = 'Sends updated privacy policy information to all active users.'

    def handle(self, *args, **options):
        users = User.objects.exclude(guest=True).exclude(is_active=False)
        template_path = Path(settings.BACKEND_ROOT) / 'templates' / 'transactional' / 'terms_of_service_update.html'
        for user in users:
            subject = 'We are updating our Terms of Service'
            ctx = {}
            to = [user.guest_email or user.email]
            from_email = settings.DEFAULT_FROM_EMAIL
            message = get_template(template_path).render(ctx)
            textifier = gen_textifier()
            msg = EmailMultiAlternatives(
                subject, textifier.handle(message), to=to, from_email=from_email, headers={'Return-Path': settings.RETURN_PATH_EMAIL}
            )
            msg.attach_alternative(message, 'text/html')
            try:
                msg.send()
            except Exception as err:
                print(f'Error for {user}: {err}')
            time.sleep(1)
