def get_client_ip(request):
    """Best-effort client IP, accounting for a reverse proxy (Render sits
    behind one, so REMOTE_ADDR alone would just show the proxy's IP)."""
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def get_or_create_guest_id(request):
    """
    Stable per-browser-session id for an anonymous visitor, stored in the
    session's data (not its key — the session key itself gets rotated by
    Django on login for security, but the data survives that rotation).
    This is what lets an anonymous visitor's earlier activity get
    reassigned to their real account once they log in — see
    security.signals.on_login_success.
    """
    guest_id = request.session.get('guest_id')
    if not guest_id:
        import secrets
        guest_id = secrets.token_hex(8)
        request.session['guest_id'] = guest_id
    return guest_id


def log_activity(request, event_type, detail=''):
    """Fire-and-forget activity log entry for the admin dashboard feed.
    Import is local to avoid a hard dependency between apps at import time."""
    from .models import ActivityEvent
    try:
        is_authenticated = bool(getattr(request, 'user', None) and request.user.is_authenticated)
        ActivityEvent.objects.create(
            event_type=event_type,
            user=request.user if is_authenticated else None,
            guest_id='' if is_authenticated else get_or_create_guest_id(request),
            detail=detail[:255],
            ip_address=get_client_ip(request),
        )
    except Exception:
        # Never let dashboard logging break the actual user-facing action.
        pass
