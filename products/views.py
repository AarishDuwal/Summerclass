from django.shortcuts import render, get_object_or_404

from .models import product, category


def products(request):
    products_qs = product.objects.filter(status=True)

    selected_category = request.GET.get('category')
    if selected_category:
        products_qs = products_qs.filter(category_id=selected_category)

    sort = request.GET.get('sort')
    if sort == 'price_asc':
        products_qs = products_qs.order_by('price')
    elif sort == 'price_desc':
        products_qs = products_qs.order_by('-price')
    elif sort == 'newest':
        products_qs = products_qs.order_by('-created_at')

    return render(request, 'NewDesign/Store.html', {
        'products': products_qs,
        'categories': category.objects.all(),
        'selected_category': int(selected_category) if selected_category else None,
        'selected_sort': sort or '',
    })


def product_detail(request, id):
    product_obj = get_object_or_404(product, id=id)
    related_products = product.objects.filter(
        category=product_obj.category, status=True
    ).exclude(id=product_obj.id)[:4]

    return render(request, 'NewDesign/product_details.html', {
        'product': product_obj,
        'related_products': related_products,
    })
