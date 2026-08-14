from django.contrib import messages
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


def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart:cart')

    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
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


def place_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, status=Order.STATUS_PENDING)

    if request.method == 'POST':
        order.status = Order.STATUS_PLACED
        order.save()
        Cart(request).clear()
        messages.success(request, f'Order #{order.id} placed successfully! We will be in touch shortly.')
        return redirect('home')

    return render(request, 'NewDesign/place-order.html', {'order': order})
