from django.urls import path
from .views import OrderListView, OrderDetailView, OrderItemDetailView, OrderCancelView, EsewaRequestView, EsewaVerificationView, EsewaErrorView

urlpatterns = [
  path('', OrderListView.as_view(), name='order_list'),
  path('<uuid:pk>', OrderDetailView.as_view(), name='order_detail'),
  path('order-items/<uuid:pk>', OrderItemDetailView.as_view(), name='order_item_detail'),
  path('order/<uuid:pk>/cancel', OrderCancelView.as_view(), name='order_cancel'),
  path('esewa-pay/<uuid:pk>/', EsewaRequestView.as_view(), name='esewa_request'),
  path('esewa-pay/verify/', EsewaVerificationView.as_view(), name='esewa_verify'),
  path('esewa-pay/<uuid:pk>/failed/', EsewaErrorView.as_view(), name='esewa_error'),
]