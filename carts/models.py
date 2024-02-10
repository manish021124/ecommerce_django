import uuid
from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product
from django.core.validators import MaxValueValidator

User = get_user_model()

# Create your models here.
class Cart(models.Model):
  id = models.UUIDField(
    primary_key = True,
    default = uuid.uuid4,
    editable = False
  )

  user = models.OneToOneField(User, on_delete=models.CASCADE)

  def __str__(self):
    return f"Cart for {self.user.username}"

  # def add_to_cart(self, product, quantity=1):
  #   # creates CartItem if doesn't exist else increases quantity to CartItem accordingly
  #   cart_item, created = CartItem.objects.get_or_create(cart=self, product=product)
  #   if not created:
  #     cart_item.quantity += quantity
  #     cart_item.save()
      
  # def update_quantity(self, product, quantity):
  #   cart_item = CartItem.objects.filter(cart=self, product=product).first()
  #   if cart_item:
  #     cart_item.quantity = quantity
  #     cart_item.save()

  # def remove_from_cart(self, product):
  #   cart_item = CartItem.objects.filter(cart=self, product=product).first()
  #   if cart_item:
  #     cart_item.delete()

  # def clear_cart(self):
  #   self.items.all().delete()


class CartItem(models.Model):
  id = models.UUIDField(
    primary_key = True,
    default = uuid.uuid4,
    editable = False
  )

  cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  quantity = models.PositiveIntegerField(default=1)
  price = models.DecimalField(max_digits=10, decimal_places=2)
  discount_percentage = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(100)])

  def __str__(self):
    return f"{self.quantity} x {self.product.name} in cart for {self.cart.user.username}"
  
  def subtotal(self):
    return self.quantity * (self.price - ((self.price * self.discount_percentage) / 100))