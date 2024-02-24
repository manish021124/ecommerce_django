from django.shortcuts import render, redirect
from django.views.generic import View, ListView, DetailView
from .models import Order, OrderItem
from carts.models import Cart, CartItem
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from user.views import CustomerGroupRequiredMixin


class OrderListView(LoginRequiredMixin, CustomerGroupRequiredMixin, ListView):
  model = Order
  template_name = 'orders/order_list.html'
  context_object_name = 'order_list'

  def get_queryset(self):
    return super().get_queryset().filter(user=self.request.user)
  
  
class OrderDetailView(LoginRequiredMixin, CustomerGroupRequiredMixin, DetailView):
  model = Order
  template_name = 'orders/order_detail.html'
  context_object_name = 'order'


class OrderItemView(LoginRequiredMixin, CustomerGroupRequiredMixin, ListView):
  model = OrderItem
  template_name = 'orders/order_item_list.html'
  context_object_name = 'order_items'

  def get_queryset(self):
    return OrderItem.objects.filter(order__user=self.request.user)
  
  
class OrderItemDetailView(LoginRequiredMixin, CustomerGroupRequiredMixin, DetailView):
  model = OrderItem
  template_name = 'orders/order_item_detail.html'
  context_object_name = 'order_item'


class CheckOutView(LoginRequiredMixin, CustomerGroupRequiredMixin, View):
  def post(self, request, *args, **kwargs):
    try:
      order = Order.objects.create(user=request.user)

      total_amount = order.calculate_total_amount()
      order.total_amount = total_amount

      order.save()

      cart_items = request.user.cart.items.all()
      for cart_item in cart_items:
        OrderItem.objects.create(
          order = order,
          product = cart_item.product,
          quantity = cart_item.quantity,
          price = cart_item.price,
          discount_percentage = cart_item.discount_percentage
        )
      # clear user's cart
      request.user.cart.items.all().delete()
      # delete the cart
      request.user.cart.delete()
      messages.success(request, 'Order added successfully.')
      return redirect('order_list')
    except Exception as e:
      messages.error(request, f"Failed to add orders: {str(e)}")
      return redirect('cart_detail')

  def get(self, request, *args, **kwargs):
    return redirect('cart_detail')