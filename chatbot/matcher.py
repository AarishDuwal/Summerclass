import re
from collections import Counter

from products.models import product as Product

# Small stopword list so common filler words in a chat message don't
# swamp the actual product-relevant keywords.
STOPWORDS = {
    'a', 'an', 'the', 'is', 'are', 'i', 'im', "i'm", 'me', 'my', 'you', 'your',
    'want', 'need', 'looking', 'look', 'for', 'show', 'find', 'find me', 'some',
    'any', 'please', 'can', 'could', 'would', 'to', 'do', 'have', 'has', 'got',
    'buy', 'sell', 'cheap', 'good', 'best', 'nice', 'like', 'and', 'or', 'of',
    'in', 'on', 'at', 'with', 'about', 'hi', 'hello', 'hey', 'thanks', 'thank',
}


def extract_keywords(message):
    words = re.findall(r"[a-zA-Z']+", message.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 2]


def find_products(message, exclude_user=None, limit=5):
    """Very lightweight recommender: score live products by how many of the
    message's keywords appear in their name/description/category, falling
    back to newest listings if nothing matches (so the bot never comes back
    empty-handed)."""
    keywords = extract_keywords(message)

    live_qs = Product.objects.filter(
        status=True, approval_status=Product.APPROVAL_APPROVED, stock__gt=0
    ).select_related('category')

    if exclude_user is not None and getattr(exclude_user, 'is_authenticated', False):
        live_qs = live_qs.exclude(owner_id=exclude_user.id)

    candidates = list(live_qs)

    if not keywords or not candidates:
        return list(live_qs.order_by('-created_at')[:limit]), 0

    scored = []
    for p in candidates:
        haystack = f"{p.name} {p.description} {p.category.name if p.category else ''}".lower()
        score = sum(1 for kw in keywords if kw in haystack)
        if score > 0:
            scored.append((score, p))

    if not scored:
        return list(live_qs.order_by('-created_at')[:limit]), 0

    scored.sort(key=lambda pair: pair[0], reverse=True)
    matched = [p for _, p in scored[:limit]]
    return matched, len(scored)


def build_reply(message, matched_count):
    keywords = extract_keywords(message)
    if matched_count == 0:
        if keywords:
            return f"I couldn't find anything matching \"{', '.join(keywords[:3])}\" right now — here's what's newest in the store instead."
        return "Here's a few things people are browsing right now — tell me what you're after and I'll narrow it down."
    return f"Here's what I found for \"{message.strip()}\":"
