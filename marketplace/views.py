from django.shortcuts import render
from products.models import product


def home(request):
    products = product.objects.filter(status=True).order_by('-created_at')
    return render(request, "NewDesign/home.html", {"products": products})
