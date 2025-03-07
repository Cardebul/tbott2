from django.db import transaction
from app.models import Cart, Product

def _add_to_cart(user, puid, qnt):
    with transaction.atomic():
        if not (product:=Product.objects.select_for_update().filter(pk=puid, quantity__gte=qnt).first()): return
        Cart.objects.create(
            user=user, product=product,
            quantity=qnt, total_cost=qnt*product.price
        )
        product.quantity -= qnt
        product.save()
        return product

def _remove_cart(cart_uid):
    with transaction.atomic():
        if not (cart:=Cart.objects.filter(pk=cart_uid).first()): return 
        if not (product:=Product.objects.select_for_update().filter(carts=cart).first()): return 
        product.quantity += cart.quantity
        product.save()
        cart.delete()
        return product