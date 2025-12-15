from django import template
from ..models import Cart

register = template.Library()

@register.simple_tag
def get_cart_count(user):
    if user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=user)
        return cart.items.count()
    return 0