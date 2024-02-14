from django.shortcuts import redirect, get_object_or_404
from django.views.generic import View, ListView, DetailView 
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Cart, CartItem
from products.models import Product
from django.contrib import messages
from django.http import JsonResponse

# Create your views here.
class CartDetailView(LoginRequiredMixin, ListView):
  template_name = 'carts/cart_detail.html'
  context_object_name = 'cart_items'

  def get_queryset(self):
    # checks if user has cart
    if hasattr(self.request.user, 'cart'):
      return self.request.user.cart.items.all()
    else:
      return CartItem.objects.none()

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    if hasattr(self.request.user, 'cart'):
      cart = self.request.user.cart
      context['cart_total'] = sum(item.subtotal() for item in self.request.user.cart.items.all())
    return context


class CartItemDetailView(LoginRequiredMixin, DetailView):
  model = CartItem
  template_name = 'carts/cart_item_detail.html'
  context_object_name = 'cart_item'


class AddToCartView(LoginRequiredMixin, View):
  def post(self, request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    # fetch price and discount_percentage from Product 
    price = product.price
    discount_percentage = product.discount_percentage

    # get user's Cart if exists else creates one
    cart, _ = Cart.objects.get_or_create(user=request.user)

    cart_item = cart.items.filter(product=product).first()
    try:
      if cart_item:
        # if user has already added that product to cart just add quantity with new quantity
        cart_item.quantity += quantity
        cart_item.save()
        messages.success(request, f"{product.name} quantity updated in your cart.")
      else:
        CartItem.objects.create(cart=cart, product=product, quantity=quantity, price=price, discount_percentage=discount_percentage)
        messages.success(request, f"{product.name} has been added to your cart.")
    except Exception as e:
      messages.error(request, f"Failed to add {product.name} to your cart. Error: {str(e)}")
      return redirect('product_detail', pk=product_id)

    return redirect('product_detail', pk=product_id)
  
  
class UpdateCartItemView(LoginRequiredMixin, View):
  def post(self, request, cart_item_id):
    cart_item = get_object_or_404(CartItem, pk=cart_item_id)
    new_quantity = int(request.POST.get('quantity'))
    
    cart_item.quantity = new_quantity
    try:
      cart_item.save()
      messages.success(request, f"Quantity of {cart_item.product.name} has been updated in your cart.")
    except Exception as e:
      messages.error(request, f"Failed to update quantity of {cart_item.product.name} in your cart.")
    return redirect('cart_detail')


class DeleteCartItemView(LoginRequiredMixin, View):
  def post(self, request, *args, **kwargs):
    cart_item_id = self.kwargs.get('cart_item_id')
    cart_item = get_object_or_404(CartItem, pk=cart_item_id)

    try:
      cart_item.delete()
      cart = cart_item.cart 
      # check if cart becomes empty and delete it if it does
      if cart.items.count() == 0:
        cart.delete()

      messages.success(request, f"{cart_item.product.name} has been removed from your cart.")
    except Exception as e:
      messages.error(request, f"Failed to remove {cart_item.product.name} from your cart. Error: {str(e)}")
    
    return redirect('cart_detail')



# add CartDeleteView, CartDeleteAllView

# show number of items in cart
class GetCartCount(View):
  def get(self, request, *args, **kwargs):
    user = request.user
    if user.is_authenticated:
      try:
        cart = Cart.objects.get(user=user)
        cart_count = cart.items.count()
        return JsonResponse({'cartCount': cart_count})
      except Cart.DoesNotExist:
        return JsonResponse({'cartCount': 0})
    else:
      return JsonResponse({'cartCount': 0})