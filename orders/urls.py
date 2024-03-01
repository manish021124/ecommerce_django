from django.urls import path
from .views import OrderListView, OrderDetailView, OrderItemDetailView, OrderCancelView

# to access url in other app
#update templates in this app as well
#{% url 'orders:name' %}
app_name = 'orders'

urlpatterns = [
  path('', OrderListView.as_view(), name='order_list'),
  path('<uuid:pk>', OrderDetailView.as_view(), name='order_detail'),
  path('order-items/<uuid:pk>', OrderItemDetailView.as_view(), name='order_item_detail'),
  path('order/<uuid:pk>/cancel', OrderCancelView.as_view(), name='order_cancel'),
]