from django.urls import path
from .views import CheckoutView, ProductDetailView, CategoryDetailView, IndexView, CartView, AddToCartView, DeleteFromCartView, ChangeQuantityView, MakeOrderView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('products/<str:ct_model>/<str:slug>/', ProductDetailView.as_view(), name='product_detail'), 
    path('category/<str:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('cart/', CartView.as_view(), name='cart'),
    path('add-to-cart/<str:ct_model>/<str:slug>/', AddToCartView.as_view(), name='add_to_cart'),
    path('remove-from-cart/<str:ct_model>/<str:slug>/', DeleteFromCartView.as_view(), name='delete_from_cart'),
    path('change_quantity/<str:ct_model>/<str:slug>', ChangeQuantityView.as_view(), name='change_quantity'),  
    path('checkout/', CheckoutView.as_view(), name='chechout'),
    path('make-order/', MakeOrderView.as_view(), name='make_order')
]
