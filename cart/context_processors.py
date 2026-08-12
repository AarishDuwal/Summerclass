from .cart import Cart


def cart_summary(request):
    """Makes the cart item count available in every template (nav badge)."""
    return {'cart_item_count': len(Cart(request))}
