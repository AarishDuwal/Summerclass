from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .models import product, category


def products(request):
    products_qs = product.objects.filter(status=True, approval_status=product.APPROVAL_APPROVED)

    selected_category = request.GET.get('category')
    if selected_category:
        products_qs = products_qs.filter(category_id=selected_category)

    keyword = request.GET.get('q', '').strip()
    if keyword:
        products_qs = products_qs.filter(name__icontains=keyword)
        from security.utils import log_activity
        log_activity(request, 'search', detail=keyword)

    sort = request.GET.get('sort')
    if sort == 'price_asc':
        products_qs = products_qs.order_by('price')
    elif sort == 'price_desc':
        products_qs = products_qs.order_by('-price')
    elif sort == 'newest':
        products_qs = products_qs.order_by('-created_at')
    else:
        products_qs = products_qs.order_by('-created_at')

    paginator = Paginator(products_qs, 12)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    # When a search turns up nothing (or very little), suggest something —
    # rather than leaving the person on a dead end.
    recommended_products = None
    if keyword and paginator.count < 4:
        seen_ids = [p.id for p in products_page]
        recommended_products = product.objects.filter(
            status=True, approval_status=product.APPROVAL_APPROVED
        ).exclude(id__in=seen_ids).order_by('-created_at')[:8]

    return render(request, 'NewDesign/Store.html', {
        'products': products_page,
        'categories': category.objects.all(),
        'selected_category': int(selected_category) if selected_category else None,
        'selected_sort': sort or '',
        'keyword': keyword,
        'recommended_products': recommended_products,
    })


def product_detail(request, id):
    product_obj = get_object_or_404(product, id=id)

    # Non-live products are only visible to their owner or staff.
    if not product_obj.is_live:
        is_owner = request.user.is_authenticated and product_obj.owner_id == request.user.id
        if not (is_owner or request.user.is_staff):
            return redirect('products')

    # Recommendations: same category first, then fill with other live
    # products so there's always something to show, not just an empty gap.
    live_qs = product.objects.filter(
        status=True, approval_status=product.APPROVAL_APPROVED
    ).exclude(id=product_obj.id)

    same_category = list(live_qs.filter(category=product_obj.category).order_by('-created_at')[:8])
    if len(same_category) < 8:
        fill_ids = [p.id for p in same_category]
        fill = live_qs.exclude(id__in=fill_ids).order_by('-created_at')[:8 - len(same_category)]
        related_products = same_category + list(fill)
    else:
        related_products = same_category

    return render(request, 'NewDesign/product_details.html', {
        'product': product_obj,
        'related_products': related_products[:4],
    })


@login_required(login_url='accounts:login')
def my_products(request):
    products_qs = product.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'NewDesign/my-products.html', {'products': products_qs})


@login_required(login_url='accounts:login')
def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price', '')
        stock = request.POST.get('stock', '1')
        category_id = request.POST.get('category')
        image = request.FILES.get('product_image')

        error = None
        if not all([name, description, price, category_id]):
            error = 'Please fill in all required fields.'
        else:
            try:
                price = float(price)
                stock = int(stock or 1)
            except ValueError:
                error = 'Price and stock must be valid numbers.'

        if error:
            messages.error(request, error)
        else:
            cat = get_object_or_404(category, id=category_id)
            product.objects.create(
                name=name,
                description=description,
                price=price,
                stock=stock,
                category=cat,
                product_image=image,
                owner=request.user,
                status=True,
                approval_status=product.APPROVAL_PENDING,
            )
            messages.success(request, f'"{name}" has been submitted and is awaiting admin approval.')
            return redirect('my_products')

    return render(request, 'NewDesign/add-product.html', {'categories': category.objects.all()})


@login_required(login_url='accounts:login')
def edit_product(request, id):
    product_obj = get_object_or_404(product, id=id, owner=request.user)

    if request.method == 'POST':
        product_obj.name = request.POST.get('name', product_obj.name).strip()
        product_obj.description = request.POST.get('description', product_obj.description).strip()
        try:
            product_obj.price = float(request.POST.get('price', product_obj.price))
            product_obj.stock = int(request.POST.get('stock', product_obj.stock))
        except ValueError:
            messages.error(request, 'Price and stock must be valid numbers.')
            return render(request, 'NewDesign/add-product.html', {
                'categories': category.objects.all(), 'product': product_obj, 'editing': True
            })

        category_id = request.POST.get('category')
        if category_id:
            product_obj.category = get_object_or_404(category, id=category_id)

        if request.FILES.get('product_image'):
            product_obj.product_image = request.FILES['product_image']

        # Edits go back into review rather than silently staying "approved".
        product_obj.approval_status = product.APPROVAL_PENDING
        product_obj.save()
        messages.success(request, f'"{product_obj.name}" was updated and is awaiting re-approval.')
        return redirect('my_products')

    return render(request, 'NewDesign/add-product.html', {
        'categories': category.objects.all(), 'product': product_obj, 'editing': True
    })


@login_required(login_url='accounts:login')
def toggle_product_status(request, id):
    product_obj = get_object_or_404(product, id=id, owner=request.user)
    product_obj.status = not product_obj.status
    product_obj.save()
    return redirect('my_products')
