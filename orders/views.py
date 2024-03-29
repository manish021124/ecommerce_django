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
from user.forms import AddressRadioForm
from user.models import Address
from .forms import PaymentMethodAddForm
from django.http import HttpResponseRedirect
import json
import base64

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
    # retrieve addresses belonging to the current user
    addresses = request.user.address_set.all()
    return render(request, self.template_name, {'addresses': addresses, 'address_form': AddressRadioForm(), 'payment_form': PaymentMethodAddForm()})
  
  def post(self, request, *args, **kwargs):
    try:
      if 'confirm_order' in request.POST:        
        address_id = request.POST.get('selected_address')
        payment_form = PaymentMethodAddForm(request.POST)
        if address_id and payment_form.is_valid():
          order = Order.objects.create(user=request.user)
          payment_method = payment_form.cleaned_data['payment_method']

          total_amount = order.calculate_total_amount()
          order.total_amount = total_amount
          address = Address.objects.get(pk=address_id)
          order.shipping_address = address
          order.payment_method = payment_method
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
          if payment_method == 'Esewa':
            return redirect('esewa_request', pk=order.id)
          else:
            return redirect('/orders/')
        else:
          messages.error(request, 'Please select a shipping address.')
          return redirect('checkout')
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


class EsewaRequestView(View):
  template_name = 'esewa/request.html'

  def get(self, request, *args, **kwargs):
    order_id = kwargs.get('pk')
    order = get_object_or_404(Order, pk=order_id)
    context = {
      'order': order,
    }
    return render(request, self.template_name, context)


class EsewaVerificationView(View):
  def get(self, request, *args, **kwargs):
    data_value = request.GET.get('data') # encrypted data from url
    decoded_data = base64.b64decode(data_value).decode('utf-8')
    map_data = json.loads(decoded_data) # convert into dictionary
    order_id = map_data.get('transaction_uuid') # get order id which is stored in transaction_uuid
    status = map_data.get('status')
    order = get_object_or_404(Order, pk=order_id)
    if status == "COMPLETE":
      order.payment_completed = True
      order.save()
        
    return redirect('/orders/')


class EsewaErrorView(View):
  template_name = 'esewa/error.html'

  def get(self, request, *args, **kwargs):
    return render(request, self.template_name)