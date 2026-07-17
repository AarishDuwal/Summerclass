from django.shortcuts import render, get_object_or_404
from .models import product,category

def products(request):
    return render(request, 'products/products.html')

def product_detail(request,id):
    get_product = get_object_or_404(product, id=id)
    return render(request, 'products/details.html', {'get_product': get_product})