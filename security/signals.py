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
    _claim_guest_activity(request, user)


def _claim_guest_activity(request, user):
    """Retag this browser session's pre-login anonymous activity (searches,
    add-to-cart, etc.) with the account that just logged in, so the
    dashboard shows the real username instead of a guest label going
    forward. The guest_id survives Django's session-key rotation on login
    because it's stored in the session's data, not its key."""
    if request is None:
        return
    guest_id = request.session.get('guest_id')
    if not guest_id:
        return
    from .models import ActivityEvent
    ActivityEvent.objects.filter(guest_id=guest_id, user__isnull=True).update(user=user, guest_id='')


def on_login_failed(sender, credentials, request=None, **kwargs):
    # `credentials` holds whatever the login form submitted — usually
    # 'username' or 'email' depending on the form, never the password.
    username = credentials.get('username') or credentials.get('email') or ''
    _log_attempt(request, username, success=False)


user_logged_in.connect(on_login_success)
user_login_failed.connect(on_login_failed)
