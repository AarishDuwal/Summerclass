import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Creates a superuser from environment variables if one doesn't already
    exist. Safe to run on every deploy (idempotent) — intended for hosts
    like Render's free tier where there's no interactive shell access.

    Reads:
        DJANGO_SUPERUSER_USERNAME
        DJANGO_SUPERUSER_EMAIL
        DJANGO_SUPERUSER_PASSWORD

    If any are unset, the command does nothing (so it's safe to leave
    wired into the start command permanently).
    """

    help = "Create a superuser from env vars if it doesn't already exist."

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not all([username, email, password]):
            self.stdout.write('DJANGO_SUPERUSER_* env vars not set — skipping.')
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(f'Superuser "{username}" already exists — skipping.')
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f'Created superuser "{username}".'))
