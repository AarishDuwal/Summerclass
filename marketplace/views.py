from django.shortcuts import render
from products.models import product


def home(request):
    products = product.objects.all()
    return render(request, "home/home.html", {"products": products})