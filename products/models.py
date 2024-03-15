import uuid
from django.db import models
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Category(models.Model):
  id = models.UUIDField(
    primary_key = True,
    default = uuid.uuid4,
    editable = False
  )
  name = models.CharField(max_length=255)
  description = models.TextField(blank=True)
  parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

  class Meta:
    verbose_name_plural = 'Categories'

  def __str__(self):
    return self.name

  # for displaying parent categories in product_detail
  def get_ancestors(self):
    ancestors = []
    current = self.parent
    while current:
      ancestors.insert(0, current)
      current = current.parent
    return ancestors


class Product(models.Model):
  # implementing UUIDs
  id = models.UUIDField(
    primary_key = True,
    default = uuid.uuid4,
    editable = False
  )
  name = models.CharField(max_length=255)
  description = models.TextField()
  price = models.DecimalField(max_digits=10, decimal_places=2)
  discount_percentage = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(100)])
  stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
  category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
  store = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'groups__name': 'store'})
  is_deleted = models.BooleanField(default=False) #soft deletion flag

  def __str__(self):
    return self.name

  # for setting canonical url 
  def get_absolute_url(self):
    return reverse('product_detail', args=[str(self.id)])

  def total_amount(self):
    return self.price - ((self.price * self.discount_percentage) / 100)

  # override default delete function
  def delete(self, using=None, keep_parents=False):
    from carts.models import CartItem
    self.is_deleted = True
    self.save()
    cart_items = CartItem.objects.filter(product=self.id) # retrieve cartitems related to product
    for cart_item in cart_items:
      cart = cart_item.cart # gets cart of related cartitems
      cart_item.delete()
      if cart.items.count() == 0: # if cart doesn't have any items
        cart.delete()
  

class ProductImage(models.Model):
  id = models.UUIDField(
    primary_key = True,
    default = uuid.uuid4,
    editable = False
  )
  product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
  image = models.ImageField(upload_to='images/')

  def __str__(self):
    return f"Image for {self.product.name}"


class Review(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'groups__name': 'customer'})
  order_item = models.ForeignKey('orders.OrderItem', on_delete=models.CASCADE, limit_choices_to={'order__status': 'Delivered'}) # used order.OrderItem cause using OrderItem directly creates circular import
  rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
  review =  models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"Review for {self.order_item.product.name} of order {self.order_item.order.order_number} by {self.user.username}"
  