from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View, ListView, DetailView
from .models import Order, OrderItem
from products.models import Product
from carts.models import Cart, CartItem
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from user.views import CustomerGroupRequiredMixin
from django.contrib.auth.models import Group
from django.db.models import Q, Count


class OrderListView(LoginRequiredMixin, ListView):
  model = Order
  template_name = 'orders/order_list.html'
  context_object_name = 'order_list'
  
  def get_queryset(self):
    user = self.request.user
    if user.groups.filter(name='customer').exists():
      # For customers, retrieve orders related to the current user
      return Order.objects.filter(user=user).order_by('-date_ordered')
    elif user.groups.filter(name='store').exists():
      # For stores, retrieve orders related to the products created by that store
      # Get the products created by the store
      products = Product.objects.filter(store=user)
     # Retrive orders related to these products 
      return Order.objects.filter(items__product__in=products).distinct().order_by('-date_ordered')
    else:
      return Order.objects.none()

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    user = self.request.user
    context['pending_orders'] = self.get_queryset().filter(status='Pending')
    context['processing_orders'] = self.get_queryset().filter(status='Processing')
    context['shipped_orders'] = self.get_queryset().filter(status='Shipped') 
    context['delivered_orders'] = self.get_queryset().filter(status='Delivered') 
    context['cancelled_orders'] = self.get_queryset().filter(status='Cancelled') 
    return context
  
  
class OrderDetailView(LoginRequiredMixin, DetailView):
  model = Order
  template_name = 'orders/order_detail.html'
  context_object_name = 'order'

  # if user is store just display products created by that store in that order
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    order = self.get_object()
    user = self.request.user
    if user.groups.filter(name='store').exists():
      order_items = order.items.filter(product__store=user)
    else:
      order_items = order.items.all()
    context['order_items'] = order_items
    return context


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
      return redirect('/orders/')
    except Exception as e:
      messages.error(request, f"Failed to add orders: {str(e)}")
      return redirect('cart_detail')