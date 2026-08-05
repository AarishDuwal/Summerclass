from django.shortcuts import render
from products.models import product


def home(request):
    products = product.objects.all()
    return render(request, "NewDesign/home.html", {"products": products})