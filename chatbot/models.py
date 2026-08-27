from django.conf import settings
from django.db import models


class ChatQuery(models.Model):
    """Logs every question asked to the recommendation chatbot — lets an
    admin see what shoppers are actually looking for (and whether the
    catalog is missing something people keep asking about)."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    session_key = models.CharField(max_length=40, blank=True)
    message = models.TextField()
    matched_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        who = self.user.email if self.user else f'guest ({self.session_key[:8]})'
        return f'{who}: {self.message[:50]}'
