from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from cart.models import Order, OrderItem
from products.models import product as Product

from .models import Message, Profile, ProductRequest


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        user = User.objects.filter(email__iexact=email).first()

        if user is None:
            messages.error(request, 'Invalid email or password.')
        elif not user.is_active:
            messages.error(request, 'Your account is pending activation by an admin. Please check back later.')
        else:
            auth_user = authenticate(request, username=user.username, password=password)
            if auth_user is not None:
                login(request, auth_user)
                messages.success(request, f'Welcome back, {auth_user.first_name or auth_user.username}!')
                next_url = request.POST.get('next') or request.GET.get('next') or 'accounts:dashboard'
                return redirect(next_url)
            messages.error(request, 'Invalid email or password.')

    return render(request, 'NewDesign/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        error = None
        if not all([first_name, last_name, email, password, confirm_password]):
            error = 'Please fill in all required fields.'
        elif password != confirm_password:
            error = 'Passwords do not match.'
        elif User.objects.filter(email__iexact=email).exists():
            error = 'An account with that email already exists.'
        else:
            try:
                validate_password(password)
            except ValidationError as exc:
                error = ' '.join(exc.messages)

        if error:
            messages.error(request, error)
        else:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=False,  # requires admin activation before login
            )
            Profile.objects.create(user=user, phone_number=phone_number)
            messages.success(
                request,
                'Your account has been created! An admin needs to activate it before you can log in — please check back soon.'
            )
            return redirect('accounts:login')

    return render(request, 'NewDesign/register.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required(login_url='accounts:login')
def dashboard(request):
    my_products = Product.objects.filter(owner=request.user)
    my_orders = Order.objects.filter(user=request.user)
    my_sales_items = OrderItem.objects.filter(product__owner=request.user)

    context = {
        'my_products_count': my_products.count(),
        'my_orders_count': my_orders.count(),
        'my_sales_count': my_sales_items.values('order').distinct().count(),
        'products_total': my_products.count(),
        'products_approved': my_products.filter(approval_status=Product.APPROVAL_APPROVED).count(),
        'products_pending': my_products.filter(approval_status=Product.APPROVAL_PENDING).count(),
        'products_active': my_products.filter(status=True).count(),
        'products_inactive': my_products.filter(status=False).count(),
    }
    return render(request, 'NewDesign/dashboard.html', context)


@login_required(login_url='accounts:login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'NewDesign/my-orders.html', {'orders': orders})


@login_required(login_url='accounts:login')
def my_sales(request):
    sale_items = OrderItem.objects.filter(product__owner=request.user).select_related('order', 'product').order_by('-order__created_at')
    return render(request, 'NewDesign/my-sales.html', {'sale_items': sale_items})


@login_required(login_url='accounts:login')
def requests_sent(request):
    sent = ProductRequest.objects.filter(sender=request.user).select_related('product', 'receiver')
    return render(request, 'NewDesign/requests-sent.html', {'requests_list': sent})


@login_required(login_url='accounts:login')
def requests_received(request):
    received = ProductRequest.objects.filter(receiver=request.user).select_related('product', 'sender')
    return render(request, 'NewDesign/requests-received.html', {'requests_list': received})


@login_required(login_url='accounts:login')
def request_respond(request, request_id, action):
    req = get_object_or_404(ProductRequest, id=request_id, receiver=request.user)
    if action == 'accept':
        req.status = ProductRequest.STATUS_ACCEPTED
        messages.success(request, 'Request accepted.')
    elif action == 'decline':
        req.status = ProductRequest.STATUS_DECLINED
        messages.info(request, 'Request declined.')
    req.save()
    return redirect('accounts:requests_received')


@login_required(login_url='accounts:login')
def send_product_request(request, product_id):
    product_obj = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        if product_obj.owner_id == request.user.id:
            messages.error(request, "You can't send a request on your own product.")
        else:
            ProductRequest.objects.create(
                sender=request.user,
                receiver=product_obj.owner,
                product=product_obj,
                message=request.POST.get('message', ''),
            )
            messages.success(request, f'Your request about "{product_obj.name}" has been sent.')
    return redirect('product_detail', id=product_obj.id)


@login_required(login_url='accounts:login')
def messages_inbox(request):
    inbox = Message.objects.filter(recipient=request.user)
    return render(request, 'NewDesign/messages-inbox.html', {'message_list': inbox})


@login_required(login_url='accounts:login')
def messages_sent(request):
    sent = Message.objects.filter(sender=request.user)
    return render(request, 'NewDesign/messages-sent.html', {'message_list': sent})


@login_required(login_url='accounts:login')
def message_mark_read(request, message_id):
    msg = get_object_or_404(Message, id=message_id, recipient=request.user)
    msg.is_read = True
    msg.save()
    return redirect('accounts:messages_inbox')


@login_required(login_url='accounts:login')
def send_message(request, recipient_id):
    recipient = get_object_or_404(User, id=recipient_id)
    if request.method == 'POST':
        if recipient.id == request.user.id:
            messages.error(request, "You can't message yourself.")
        else:
            Message.objects.create(
                sender=request.user,
                recipient=recipient,
                subject=request.POST.get('subject', ''),
                body=request.POST.get('body', ''),
            )
            messages.success(request, f'Message sent to {recipient.first_name or recipient.username}.')
        return redirect('accounts:messages_sent')
    return render(request, 'NewDesign/message-compose.html', {'recipient': recipient})


@login_required(login_url='accounts:login')
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '').strip()
        request.user.last_name = request.POST.get('last_name', '').strip()
        request.user.email = request.POST.get('email', '').strip()
        request.user.save()
        profile.phone_number = request.POST.get('phone_number', '').strip()
        profile.save()
        messages.success(request, 'Profile updated.')
        return redirect('accounts:edit_profile')
    return render(request, 'NewDesign/edit-profile.html', {'profile': profile})


@login_required(login_url='accounts:login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
        elif new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
        else:
            try:
                validate_password(new_password, user=request.user)
            except ValidationError as exc:
                messages.error(request, ' '.join(exc.messages))
            else:
                request.user.set_password(new_password)
                request.user.save()
                login(request, request.user)  # keep the session alive after password change
                messages.success(request, 'Password changed successfully.')
                return redirect('accounts:dashboard')

    return render(request, 'NewDesign/change-password.html')
