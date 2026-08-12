from decimal import Decimal

from products.models import product as Product

CART_SESSION_KEY = 'cart'


class Cart:
    """A simple session-backed shopping cart.

    Stored in the session as: {"<product_id>": {"quantity": <int>}}
    Keeping only the product id + quantity in the session (not price)
    means price/stock changes on the product are always picked up fresh.
    """

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def add(self, product_obj, quantity=1, replace=False):
        product_id = str(product_obj.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0}

        if replace:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        # Never let the cart hold more than what's in stock, or drop to 0.
        max_qty = max(product_obj.stock, 0)
        self.cart[product_id]['quantity'] = min(self.cart[product_id]['quantity'], max_qty)
        if self.cart[product_id]['quantity'] <= 0:
            self.remove(product_obj)
        else:
            self.save()

    def remove(self, product_obj):
        product_id = str(product_obj.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        self.session[CART_SESSION_KEY] = {}
        self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        products_by_id = {str(p.id): p for p in products}

        # Drop stale entries for products that no longer exist.
        for product_id in list(self.cart.keys()):
            if product_id not in products_by_id:
                del self.cart[product_id]
        self.save()

        for product_id, item in self.cart.items():
            product_obj = products_by_id[product_id]
            quantity = item['quantity']
            yield {
                'product': product_obj,
                'quantity': quantity,
                'price': Decimal(str(product_obj.price)),
                'subtotal': Decimal(str(product_obj.price)) * quantity,
            }

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_subtotal(self):
        return sum((item['subtotal'] for item in self), Decimal('0'))
