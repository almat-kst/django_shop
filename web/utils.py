from django.db import models

def recalc_cart(cart):
    cart_data = cart.products.aggregate(models.Sum('final_price'), models.Count('id'))
    if cart_data.get('final_price__sum'):
        final_price = cart_data.get('final_price__sum')
    else:
        final_price = 0
    total_products = cart_data['id__count']
    cart.save()