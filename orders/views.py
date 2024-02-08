from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Order, OrderItem
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
class OrderListView(LoginRequiredMixin, ListView):
  model = Order
  template_name = 'orders/order_list.html'
  context_object_name = 'order_list'

  def get_queryset(self):
    return super().get_queryset().filter(user=self.request.user)
  
  
class OrderDetailView(LoginRequiredMixin, DetailView):
  model = Order
  template_name = 'orders/order_detail.html'
  context_object_name = 'order'


class OrderItemView(LoginRequiredMixin, ListView):
  model = OrderItem
  template_name = 'orders/order_item_list.html'
  context_object_name = 'order_items'

  def get_queryset(self):
    return OrderItem.objects.filter(order__user=self.request.user)
  
  
class OrderItemDetailView(LoginRequiredMixin, DetailView):
  model = OrderItem
  template_name = 'orders/order_item_detail.html'
  context_object_name = 'order_item'
