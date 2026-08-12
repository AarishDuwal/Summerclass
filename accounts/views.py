from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from .models import Profile


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        user = User.objects.filter(email__iexact=email).first()
        auth_user = authenticate(request, username=user.username, password=password) if user else None

        if auth_user is not None:
            login(request, auth_user)
            messages.success(request, f'Welcome back, {auth_user.first_name or auth_user.username}!')
            next_url = request.POST.get('next') or request.GET.get('next') or 'home'
            return redirect(next_url)

        messages.error(request, 'Invalid email or password.')

    return render(request, 'NewDesign/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

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
        elif len(password) < 8:
            error = 'Password must be at least 8 characters long.'

        if error:
            messages.error(request, error)
        else:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            Profile.objects.create(user=user, phone_number=phone_number)
            login(request, user)
            messages.success(request, f'Welcome, {first_name}! Your account has been created.')
            return redirect('home')

    return render(request, 'NewDesign/register.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')
