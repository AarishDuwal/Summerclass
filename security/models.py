from django.db import models


class LoginAttempt(models.Model):
    """Audit log of every login attempt sitewide — including the Django
    admin's own login page, since it's wired via Django's global auth
    signals rather than any single view. Read-only in admin (see admin.py):
    this is a forensic record, not something anyone should be able to edit.
    """
    username = models.CharField(max_length=150, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    path = models.CharField(max_length=255, blank=True)
    success = models.BooleanField(default=False)
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-attempted_at']

    def __str__(self):
        outcome = 'succeeded' if self.success else 'failed'
        return f'{self.username or "unknown"} @ {self.ip_address} {outcome} on {self.path}'
