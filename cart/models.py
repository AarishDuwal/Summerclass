from django.conf import settings
from django.db import models

from products.models import product as Product


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PLACED = 'placed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending payment'),
        (STATUS_PLACED, 'Placed'),
    ]

    PAYMENT_ESEWA = 'esewa'
    PAYMENT_KHALTI = 'khalti'
    PAYMENT_CHOICES = [
        (PAYMENT_ESEWA, 'eSewa'),
        (PAYMENT_KHALTI, 'Khalti'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, blank=True)
    gateway_ref = models.CharField(
        max_length=100, blank=True, db_index=True,
        help_text='eSewa transaction_uuid or Khalti pidx for this order.'
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    order_note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order #{self.id} ({self.get_status_display()})'

    @property
    def subtotal(self):
        return sum((item.subtotal for item in self.items.all()), 0)

    @property
    def tax(self):
        return round(float(self.subtotal) * 0.02, 2)

    @property
    def total(self):
        return round(float(self.subtotal) + self.tax, 2)


class OrderItem(models.Model):
    FULFILLMENT_PROCESSING = 'processing'
    FULFILLMENT_SHIPPED = 'shipped'
    FULFILLMENT_DELIVERED = 'delivered'
    FULFILLMENT_CANCELLED = 'cancelled'
    FULFILLMENT_CHOICES = [
        (FULFILLMENT_PROCESSING, 'Processing'),
        (FULFILLMENT_SHIPPED, 'Shipped'),
        (FULFILLMENT_DELIVERED, 'Delivered'),
        (FULFILLMENT_CANCELLED, 'Cancelled'),
    ]

    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    fulfillment_status = models.CharField(
        max_length=20, choices=FULFILLMENT_CHOICES, default=FULFILLMENT_PROCESSING
    )

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f'{self.quantity} x {self.product_name}'
