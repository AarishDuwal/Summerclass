from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from products.models import product as Product

from .cart import Cart
from .models import Order, OrderItem


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'NewDesign/cart.html', {'cart': cart})


@require_POST
def cart_add(request, product_id):
    product_obj = get_object_or_404(Product, id=product_id)
    next_url = request.POST.get('next') or 'cart:cart'

    is_owner = request.user.is_authenticated and product_obj.owner_id == request.user.id
    if not product_obj.is_live and not (is_owner or request.user.is_staff):
        messages.error(request, 'This product is not currently available.')
        return redirect(next_url)

    if product_obj.stock <= 0:
        messages.error(request, f'"{product_obj.name}" is out of stock.')
        return redirect(next_url)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1

    cart = Cart(request)
    cart.add(product_obj, quantity=quantity)
    messages.success(request, f'Added "{product_obj.name}" to your cart.')
    return redirect(next_url)


@require_POST
def cart_update(request, product_id):
    product_obj = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1
    cart.add(product_obj, quantity=quantity, replace=True)
    return redirect('cart:cart')


def cart_remove(request, product_id):
    product_obj = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    cart.remove(product_obj)
    messages.info(request, f'Removed "{product_obj.name}" from your cart.')
    return redirect('cart:cart')


@login_required(login_url='accounts:login')
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart:cart')

    if request.method == 'POST':
        # Re-check stock at checkout time — it may have changed since items were added.
        for item in cart:
            if item['quantity'] > max(item['product'].stock, 0):
                messages.error(
                    request,
                    f'Only {max(item["product"].stock, 0)} of "{item["product"].name}" left in stock. '
                    'Please update your cart.'
                )
                return redirect('cart:cart')

        order = Order.objects.create(
            user=request.user,
            first_name=request.POST.get('first_name', ''),
            last_name=request.POST.get('last_name', ''),
            email=request.POST.get('email', ''),
            phone=request.POST.get('phone', ''),
            address_line_1=request.POST.get('address_line_1', ''),
            address_line_2=request.POST.get('address_line_2', ''),
            city=request.POST.get('city', ''),
            state=request.POST.get('state', ''),
            country=request.POST.get('country', ''),
            order_note=request.POST.get('order_note', ''),
        )
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                product_name=item['product'].name,
                price=item['price'],
                quantity=item['quantity'],
            )
        return redirect('cart:place_order', order_id=order.id)

    return render(request, 'NewDesign/checkout.html', {'cart': cart})


@login_required(login_url='accounts:login')
def place_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, status=Order.STATUS_PENDING, user=request.user)

    if request.method == 'POST':
        with transaction.atomic():
            # Lock the rows so two people can't both buy the last unit at once.
            for item in order.items.select_related('product').select_for_update():
                if item.product is None:
                    continue
                if item.quantity > max(item.product.stock, 0):
                    messages.error(
                        request,
                        f'Sorry, "{item.product_name}" no longer has enough stock to fulfil this order.'
                    )
                    return redirect('cart:cart')

            for item in order.items.select_related('product').select_for_update():
                if item.product is not None:
                    item.product.stock -= item.quantity
                    item.product.save(update_fields=['stock'])

            order.status = Order.STATUS_PLACED
            order.save()

        Cart(request).clear()
        messages.success(request, f'Order #{order.id} placed successfully! We will be in touch shortly.')
        return redirect('home')

    return render(request, 'NewDesign/place-order.html', {'order': order})
