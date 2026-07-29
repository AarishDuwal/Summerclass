from django.shortcuts import render, get_object_or_404
from .models import product


def products(request):
    products = product.objects.all()

    return render(request, 'products/products.html', {
        'products': products,
    })


def product_detail(request, id):
    product_obj = get_object_or_404(product, id=id)

    return render(request, 'products/details.html', {
        'product': product_obj,
    })