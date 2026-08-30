from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from cart.cart import Cart
from cart.models import Order

from . import utils


def _fulfil_order(order, request=None):
    """Decrement stock and mark the order placed. Called only after a
    payment gateway has confirmed the money actually moved."""
    with transaction.atomic():
        for item in order.items.select_related('product').select_for_update():
            if item.product is not None:
                item.product.stock = max(item.product.stock - item.quantity, 0)
                item.product.save(update_fields=['stock'])
        order.status = Order.STATUS_PLACED
        order.save(update_fields=['status'])

    if request is not None:
        from security.utils import log_activity
        log_activity(
            request, 'order_placed',
            detail=f'Order #{order.id} - Rs. {order.total} via {order.get_payment_method_display()}'
        )


@login_required(login_url='accounts:login')
def choose_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, status=Order.STATUS_PENDING, user=request.user)
    return render(request, 'payments/choose.html', {'order': order})


@login_required(login_url='accounts:login')
def cod_confirm(request, order_id):
    order = get_object_or_404(Order, id=order_id, status=Order.STATUS_PENDING, user=request.user)

    if request.method == 'POST':
        order.payment_method = Order.PAYMENT_COD
        order.save(update_fields=['payment_method'])
        _fulfil_order(order, request)
        Cart(request).clear()
        messages.success(request, f'Order #{order.id} placed successfully! Pay in cash when it arrives.')
        return redirect('home')

    return render(request, 'payments/cod_confirm.html', {'order': order})


# ---------------------------------------------------------------------------
# eSewa
# ---------------------------------------------------------------------------

@login_required(login_url='accounts:login')
def esewa_start(request, order_id):
    order = get_object_or_404(Order, id=order_id, status=Order.STATUS_PENDING, user=request.user)
    fields, transaction_uuid = utils.esewa_payment_form_fields(order)
    order.payment_method = Order.PAYMENT_ESEWA
    order.gateway_ref = transaction_uuid
    order.save(update_fields=['payment_method', 'gateway_ref'])
    return render(request, 'payments/esewa_redirect.html', {
        'action_url': 'https://rc-epay.esewa.com.np/api/epay/main/v2/form',
        'fields': fields,
    })


def esewa_success(request):
    encoded = request.GET.get('data')
    payload = utils.esewa_verify_callback(encoded) if encoded else None
    if not payload:
        messages.error(request, 'Payment could not be verified. Please contact support if you were charged.')
        return redirect('cart:cart')

    order = get_object_or_404(Order, gateway_ref=payload['transaction_uuid'])
    if order.status == Order.STATUS_PLACED:
        return redirect('home')  # already processed (e.g. user refreshed)

    if not utils.esewa_check_status(payload['transaction_uuid'], payload['total_amount']):
        messages.error(request, 'Payment could not be confirmed with eSewa. Please contact support.')
        return redirect('cart:cart')

    _fulfil_order(order, request)
    Cart(request).clear()
    messages.success(request, f'Order #{order.id} placed successfully! Payment received via eSewa.')
    return redirect('home')


def esewa_failure(request):
    messages.error(request, 'eSewa payment was cancelled or failed. Your order has not been placed.')
    return redirect('cart:cart')


# ---------------------------------------------------------------------------
# Khalti
# ---------------------------------------------------------------------------

@login_required(login_url='accounts:login')
def khalti_start(request, order_id):
    order = get_object_or_404(Order, id=order_id, status=Order.STATUS_PENDING, user=request.user)
    payment_url, pidx = utils.khalti_initiate(order, request)
    if not payment_url:
        messages.error(request, 'Could not start Khalti payment right now. Please try again.')
        return redirect('cart:place_order', order_id=order.id)

    order.payment_method = Order.PAYMENT_KHALTI
    order.gateway_ref = pidx
    order.save(update_fields=['payment_method', 'gateway_ref'])
    return redirect(payment_url)


def khalti_callback(request):
    pidx = request.GET.get('pidx')
    if not pidx:
        messages.error(request, 'Payment could not be verified. Please contact support if you were charged.')
        return redirect('cart:cart')

    order = get_object_or_404(Order, gateway_ref=pidx)
    if order.status == Order.STATUS_PLACED:
        return redirect('home')

    ok, _data = utils.khalti_lookup(pidx)
    if not ok:
        messages.error(request, 'Khalti payment was not completed. Your order has not been placed.')
        return redirect('cart:cart')

    _fulfil_order(order, request)
    Cart(request).clear()
    messages.success(request, f'Order #{order.id} placed successfully! Payment received via Khalti.')
    return redirect('home')
