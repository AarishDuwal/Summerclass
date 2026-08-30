"""
Adds a small "at a glance" stats strip to the top of the Django admin
dashboard: user/product/order counts and total revenue. Deliberately does
NOT duplicate detailed lists here — Recent Orders live under Cart > Orders,
and login attempts / site activity live under Security > Login attempts
and Security > Activity events in the sidebar, where they get proper
search, filtering, and pagination that a hand-rolled dashboard table can't
match. Keeping the dashboard itself light stops it turning into a second,
worse copy of those pages.

Implemented by pointing AdminSite.index_template at our own template
(which extends the real admin/index.html and injects one extra block) and
wrapping AdminSite.index() so it computes the extra context. This avoids
having to subclass AdminSite and re-register every model against a new
site instance.
"""
import types

from django.contrib import admin
from django.contrib.admin.sites import AdminSite


def _dashboard_context():
    # Local imports: this module is loaded from apps.ready(), which runs
    # before every app's models are guaranteed importable elsewhere.
    from django.contrib.auth.models import User
    from products.models import product as Product
    from cart.models import Order

    placed_orders = Order.objects.filter(status=Order.STATUS_PLACED)
    total_revenue = sum((o.total for o in placed_orders), 0)

    return {
        'dash_stats': {
            'total_users': User.objects.count(),
            'total_products': Product.objects.count(),
            'pending_products': Product.objects.filter(
                approval_status=Product.APPROVAL_PENDING
            ).count(),
            'total_orders': placed_orders.count(),
            'total_revenue': round(total_revenue, 2),
        },
    }


def _custom_index(self, request, extra_context=None):
    extra_context = extra_context or {}
    extra_context.update(_dashboard_context())
    return AdminSite.index(self, request, extra_context)


def install_custom_dashboard():
    admin.site.index_template = 'admin/custom_dashboard.html'
    admin.site.index = types.MethodType(_custom_index, admin.site)
