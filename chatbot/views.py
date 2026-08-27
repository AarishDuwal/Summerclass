import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from .matcher import build_reply, find_products
from .models import ChatQuery


@require_POST
@csrf_protect
def chat_message(request):
    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        data = {}
    message = (data.get('message') or request.POST.get('message') or '').strip()

    if not message:
        return JsonResponse({'reply': "Say something and I'll try to help!", 'products': []})

    if not request.session.session_key:
        request.session.create()

    matched, matched_count = find_products(
        message,
        exclude_user=request.user if request.user.is_authenticated else None,
    )

    ChatQuery.objects.create(
        user=request.user if request.user.is_authenticated else None,
        session_key=request.session.session_key or '',
        message=message[:2000],
        matched_count=matched_count,
    )

    products_payload = [
        {
            'id': p.id,
            'name': p.name,
            'price': str(p.price),
            'url': f'/products/{p.id}/',
            'image_url': p.product_image.url if p.product_image else '',
        }
        for p in matched
    ]

    return JsonResponse({
        'reply': build_reply(message, matched_count),
        'products': products_payload,
    })
