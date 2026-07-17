from django.shortcuts import render
from django.http import HttpResponse
from products.models import category, product

def home(request):
    products = product.objects.all()
    return render(request, 'home/home.html', {'products': products})