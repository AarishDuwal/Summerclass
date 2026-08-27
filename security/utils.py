def get_client_ip(request):
    """Best-effort client IP, accounting for a reverse proxy (Render sits
    behind one, so REMOTE_ADDR alone would just show the proxy's IP)."""
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')
