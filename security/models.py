from django.conf import settings
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
    is_honeypot = models.BooleanField(
        default=False,
        help_text='True if this hit the decoy /admin/ login rather than the real admin.'
    )
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-attempted_at']

    def __str__(self):
        outcome = 'succeeded' if self.success else 'failed'
        tag = ' [HONEYPOT]' if self.is_honeypot else ''
        return f'{self.username or "unknown"} @ {self.ip_address} {outcome} on {self.path}{tag}'


class ActivityEvent(models.Model):
    """Lightweight sitewide activity feed for the admin dashboard —
    searches, add-to-cart actions, and placed orders. Deliberately generic
    (a type + free-text detail) rather than one model per event, since
    this is purely for admins to eyeball recent activity, not to drive
    business logic."""
    SEARCH = 'search'
    ADD_TO_CART = 'add_to_cart'
    ORDER_PLACED = 'order_placed'
    EVENT_CHOICES = [
        (SEARCH, 'Search'),
        (ADD_TO_CART, 'Added to cart'),
        (ORDER_PLACED, 'Order placed'),
    ]

    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    detail = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        who = self.user.username if self.user else 'anonymous'
        return f'{self.get_event_type_display()} by {who}: {self.detail}'
