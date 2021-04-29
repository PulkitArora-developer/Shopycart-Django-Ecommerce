from django.urls import path
from . import views

urlpatterns = [
    path('',views.cart,name='cart'),
    path('add-cart/<int:product_id>/',views.add_to_cart,name='add_to_cart'),
    path('remove-cart/<int:product_id>/<int:cart_item_id>/',views.remove_items_from_cart,name='remove_items_from_cart'),
    path('remove-cart/item/all/<int:product_id>/<int:cart_item_id>/',views.remove_items_from_cart_all,name='remove_items_from_cart_all'),
    path('checkout/',views.checkout,name='checkout'),

]