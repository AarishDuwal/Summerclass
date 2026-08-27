from django.shortcuts import render

from products.models import category, product


def home(request):
    live_products = product.objects.filter(
        status=True, approval_status=product.APPROVAL_APPROVED
    ).order_by('-created_at')

    context = {
        'products': live_products,
        'categories': category.objects.all()[:8],
    }
    return render(request, "NewDesign/home.html", context)
