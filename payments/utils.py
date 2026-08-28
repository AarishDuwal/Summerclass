"""
Helpers for the eSewa (ePay v2) and Khalti (KPG-2) redirect-based checkout
flows. Both gateways follow the same shape:

    1. INITIATE  - build a signed/authenticated request, send the customer
                   to the gateway's hosted payment page.
    2. CALLBACK  - the gateway redirects the customer back to us with some
                   proof of the result in the query string / POST body.
    3. VERIFY    - never trust step 2 alone. Call the gateway's
                   server-to-server status/lookup API to confirm the
                   payment actually succeeded before fulfilling the order.
"""
import base64
import hashlib
import hmac
import json

import requests
from django.conf import settings


# ---------------------------------------------------------------------------
# eSewa (ePay v2)
# ---------------------------------------------------------------------------

def esewa_signature(total_amount, transaction_uuid, product_code):
    """HMAC-SHA256 signature eSewa expects, base64-encoded."""
    message = f'total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}'
    secret = settings.ESEWA_SETTINGS['SECRET_KEY'].encode('utf-8')
    digest = hmac.new(secret, message.encode('utf-8'), hashlib.sha256).digest()
    return base64.b64encode(digest).decode('utf-8')


def esewa_payment_form_fields(order):
    """Build the signed field set for the auto-submitting eSewa form."""
    cfg = settings.ESEWA_SETTINGS
    total_amount = f'{order.total:.2f}'
    transaction_uuid = f'order-{order.id}-{order.created_at.timestamp():.0f}'

    fields = {
        'amount': total_amount,
        'tax_amount': '0',
        'total_amount': total_amount,
        'transaction_uuid': transaction_uuid,
        'product_code': cfg['PRODUCT_CODE'],
        'product_service_charge': '0',
        'product_delivery_charge': '0',
        'success_url': cfg['SUCCESS_URL'],
        'failure_url': cfg['FAILURE_URL'],
        'signed_field_names': 'total_amount,transaction_uuid,product_code',
    }
    fields['signature'] = esewa_signature(total_amount, transaction_uuid, cfg['PRODUCT_CODE'])
    return fields, transaction_uuid


def esewa_verify_callback(encoded_data):
    """
    Decode+verify the base64 `data` query param eSewa appends to success_url.
    Returns the decoded dict if the signature checks out, else None.
    """
    try:
        decoded = base64.b64decode(encoded_data).decode('utf-8')
        payload = json.loads(decoded)
    except Exception:
        return None

    expected_sig = esewa_signature(
        payload.get('total_amount'), payload.get('transaction_uuid'), payload.get('product_code')
    )
    if not hmac.compare_digest(expected_sig, payload.get('signature', '')):
        return None
    if payload.get('status') != 'COMPLETE':
        return None
    return payload


def esewa_check_status(transaction_uuid, total_amount):
    """Server-to-server status check — defence in depth, never trust the redirect alone."""
    cfg = settings.ESEWA_SETTINGS
    try:
        resp = requests.get(
            cfg['STATUS_CHECK_URL'],
            params={
                'product_code': cfg['PRODUCT_CODE'],
                'total_amount': total_amount,
                'transaction_uuid': transaction_uuid,
            },
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json().get('status') == 'COMPLETE'
    except requests.RequestException:
        return False


# ---------------------------------------------------------------------------
# Khalti (KPG-2 ePayment)
# ---------------------------------------------------------------------------

def khalti_initiate(order, request):
    """Server-side call to start a Khalti payment. Returns (payment_url, pidx) or (None, None)."""
    cfg = settings.KHALTI_SETTINGS
    amount_paisa = int(round(order.total * 100))  # Khalti wants paisa, not rupees

    payload = {
        'return_url': cfg['RETURN_URL'],
        'website_url': cfg['WEBSITE_URL'],
        'amount': amount_paisa,
        'purchase_order_id': f'order-{order.id}',
        'purchase_order_name': f'Order #{order.id}',
        'customer_info': {
            'name': f'{order.first_name} {order.last_name}'.strip() or 'Customer',
            'email': order.email or 'customer@example.com',
            'phone': order.phone or '9800000000',
        },
    }
    try:
        resp = requests.post(
            f"{cfg['BASE_URL']}/epayment/initiate/",
            headers={'Authorization': f"Key {cfg['SECRET_KEY']}"},
            json=payload,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get('payment_url'), data.get('pidx')
    except requests.RequestException:
        return None, None


def khalti_lookup(pidx):
    """Server-to-server verification — the only source of truth for whether payment succeeded."""
    cfg = settings.KHALTI_SETTINGS
    try:
        resp = requests.post(
            f"{cfg['BASE_URL']}/epayment/lookup/",
            headers={'Authorization': f"Key {cfg['SECRET_KEY']}"},
            json={'pidx': pidx},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get('status') == 'Completed', data
    except requests.RequestException:
        return False, {}
