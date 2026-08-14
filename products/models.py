from django.conf import settings
from django.utils import timezone
from django.db import models


class category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self):
        return self.name

class product(models.Model):
    APPROVAL_PENDING = 'pending'
    APPROVAL_APPROVED = 'approved'
    APPROVAL_REJECTED = 'rejected'
    APPROVAL_CHOICES = [
        (APPROVAL_PENDING, 'Pending review'),
        (APPROVAL_APPROVED, 'Approved'),
        (APPROVAL_REJECTED, 'Rejected'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.FloatField()
    stock = models.IntegerField(default=1)
    category = models.ForeignKey(category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.BooleanField(default=0)
    product_image = models.ImageField(upload_to='photos/products', blank=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='products', null=True, blank=True,
        help_text='Seller who listed this product. Blank means it was added directly by an admin.'
    )
    approval_status = models.CharField(
        max_length=20, choices=APPROVAL_CHOICES, default=APPROVAL_APPROVED
    )

    def __str__(self):
        return self.name

    @property
    def is_live(self):
        """Visible in the storefront: active AND approved."""
        return self.status and self.approval_status == self.APPROVAL_APPROVED