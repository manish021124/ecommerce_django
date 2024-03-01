from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import View, ListView, DetailView
from .models import Order, OrderItem
from products.models import Product
from carts.models import Cart, CartItem
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from user.views import CustomerGroupRequiredMixin
from django.contrib.auth.models import Group
from django.db.models import Sum, F, ExpressionWrapper, DecimalField

class OrderListView(LoginRequiredMixin, ListView):
  model = Order
  template_name = 'orders/order_list.html'
  context_object_name = 'order_list'
  
  def get_queryset(self):
    user = self.request.user
    if user.groups.filter(name='customer').exists():
      # For customers, retrieve orders related to the current user
      # use annotate to override models total_amount for store
      return Order.objects.filter(user=user).annotate(total_amount_override=Sum('total_amount')).order_by('-date_ordered')
    elif user.groups.filter(name='store').exists():
      # For stores, retrieve orders related to the products created by that store
      # calculate total amount of products that belongs to this store only leaving products that belong to other stores
      orders = Order.objects.filter(items__product__store=user).distinct().annotate(total_amount_override=Sum(
        ExpressionWrapper(
          F('items__quantity') * (F('items__price') - (F('items__price') * F('items__discount_percentage') / 100)),
            output_field=DecimalField()
          )
        )).order_by('-date_ordered')
      return orders
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
      # total amount of displayed products only
      total_amount = sum(item.subtotal() for item in order_items)
    else:
      order_items = order.items.all()
      total_amount = order.total_amount
    context['order_items'] = order_items
    context['total_amount'] = total_amount
    return context
  
  
class OrderItemDetailView(LoginRequiredMixin, DetailView):
  model = OrderItem
  template_name = 'orders/order_item_detail.html'
  context_object_name = 'order_item'


class CheckOutView(LoginRequiredMixin, CustomerGroupRequiredMixin, View):
  template_name = 'orders/order_confirmation.html'

  def get(self, request, *args, **kwargs):
    return render(request, self.template_name)
  
  def post(self, request, *args, **kwargs):
    try:
      if 'confirm_order' in request.POST:
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
      else:
        messages.error(request, 'Please confirm your order.')
        return redirect('cart_detail')
    except Exception as e:
      messages.error(request, f"Failed to add orders: {str(e)}")
      return redirect('cart_detail')


class OrderCancelView(LoginRequiredMixin, View):
  template_name = 'orders/confirm_order_cancel.html'

  def get(self, request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, self.template_name, {'order': order})

  def post(self, request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.status in ['Pending', 'Processing']:
      order.status = 'Cancelled'
      order.save()
      messages.success(request, f'Order {order.order_number} has been cancelled successfully.')
      return redirect('/orders/')
    else:
      messages.error(request, f'Order {order.order_number} cannot be cancelled.')
    return redirect('/orders/')