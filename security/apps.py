from django.apps import AppConfig


class SecurityConfig(AppConfig):
    name = 'security'

    def ready(self):
        from . import signals  # noqa: F401 — connects the login-attempt signal handlers
        from .admin_dashboard import install_custom_dashboard
        install_custom_dashboard()
