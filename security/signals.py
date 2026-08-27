from django.contrib.auth.signals import user_logged_in, user_login_failed

from .models import LoginAttempt
from .utils import get_client_ip


def _log_attempt(request, username, success):
    if request is None:
        return
    LoginAttempt.objects.create(
        username=username or '',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        path=request.path,
        success=success,
    )


def on_login_success(sender, request, user, **kwargs):
    _log_attempt(request, getattr(user, 'email', None) or getattr(user, 'username', ''), success=True)


def on_login_failed(sender, credentials, request=None, **kwargs):
    # `credentials` holds whatever the login form submitted — usually
    # 'username' or 'email' depending on the form, never the password.
    username = credentials.get('username') or credentials.get('email') or ''
    _log_attempt(request, username, success=False)


user_logged_in.connect(on_login_success)
user_login_failed.connect(on_login_failed)
