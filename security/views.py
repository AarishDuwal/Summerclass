from django.shortcuts import render

from .models import LoginAttempt
from .utils import get_client_ip


def fake_admin_login(request, sub_path=None):
    """
    Decoy admin login sitting at the site's real /admin/ path. It never
    authenticates anyone — every visit and every submitted attempt is
    logged as a honeypot hit (username + IP + path, deliberately not the
    password), and the response always looks like an ordinary failed
    Django admin login, matching what a real one does.
    """
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '')
        LoginAttempt.objects.create(
            username=username,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            path=request.path,
            success=False,
            is_honeypot=True,
        )
        error = (
            'Please enter the correct username and password for a staff '
            'account. Note that both fields may be case-sensitive.'
        )
    else:
        # Log the mere visit too — real reconnaissance often never submits
        # a login form at all before moving on.
        LoginAttempt.objects.create(
            username='',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            path=request.path,
            success=False,
            is_honeypot=True,
        )

    return render(request, 'security/fake_admin_login.html', {'error': error})
