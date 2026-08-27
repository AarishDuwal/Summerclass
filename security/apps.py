from django.apps import AppConfig


class SecurityConfig(AppConfig):
    name = 'security'

    def ready(self):
        from . import signals  # noqa: F401 — connects the login-attempt signal handlers
