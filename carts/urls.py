from django.urls import path
from .views import CartDetailView, CartItemDetailView, AddToCartView, UpdateCartItemView, DeleteCartItemView
from orders.views import CheckOutView

urlpatterns = [
  path('', CartDetailView.as_view(), name='cart_detail'),
  path('cart-items/<uuid:pk>', CartItemDetailView.as_view(), name='cart_item_detail'),
  path('add-to-cart/<uuid:product_id>', AddToCartView.as_view(), name='add_to_cart'),
  path('cart-items/<uuid:cart_item_id>/update/', UpdateCartItemView.as_view(), name='update_cart_item'),
  path('cart-items/<uuid:cart_item_id>/delete/', DeleteCartItemView.as_view(), name='delete_cart_item'),
  path('checkout/', CheckOutView.as_view(), name='checkout'),
]