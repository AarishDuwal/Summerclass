def get_client_ip(request):
    """Best-effort client IP, accounting for a reverse proxy (Render sits
    behind one, so REMOTE_ADDR alone would just show the proxy's IP)."""
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def log_activity(request, event_type, detail=''):
    """Fire-and-forget activity log entry for the admin dashboard feed.
    Import is local to avoid a hard dependency between apps at import time."""
    from .models import ActivityEvent
    try:
        ActivityEvent.objects.create(
            event_type=event_type,
            user=request.user if getattr(request, 'user', None) and request.user.is_authenticated else None,
            detail=detail[:255],
            ip_address=get_client_ip(request),
        )
    except Exception:
        # Never let dashboard logging break the actual user-facing action.
        pass
