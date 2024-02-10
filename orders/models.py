import uuid
from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from products.models import Product
from django.utils.timezone import now
from django.utils.crypto import get_random_string
from django.db.models import Sum
from django.core.validators import MaxValueValidator

User = get_user_model()

# Create your models here.
class Order(models.Model):
  STATUS_CHOICES = (
    ('Pending', 'Pending'),
    ('Processing', 'Processing'),
    ('Shipped', 'Shipped'),
    ('Delivered', 'Delivered'),
    ('Cancelled', 'Cancelled'),
  )

  id = models.UUIDField(
    primary_key = True,
    default = uuid.uuid4,
    editable = False
  )
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  date_ordered = models.DateTimeField(default=now)
  status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
  total_amount = models.DecimalField(max_digits=10, decimal_places=2)
  order_number = models.CharField(max_length=20, unique=True, editable=False)

  def __str__(self):
    return f"Order #{self.order_number} - {self.user.username}"

  def get_absolute_url(self):
    return reverse('order_detail', args=[str(self.id)])

  def calculate_total_amount(self):
    total_amount = self.items.aggregate(total_amount=Sum('subtotal'))['total_amount']
    return total_amount or 0

  # ensures order_number is populated with unique order number
  def save(self, *args, **kwargs):
    if not self.order_number:
      self.order_number = generate_order_number()

    # calculate total amount based on order items 
    self.total_amount = self.calculate_total_amount()

    super().save(*args, **kwargs)


# generates unique order number
def generate_order_number():
  timestamp = now().strftime('%Y%m%d%H%M%S')
  random_string = get_random_string(length=6)
  return f'{timestamp}-{random_string}'
  

class OrderItem(models.Model):
  id = models.UUIDField(
    primary_key = True,
    default = uuid.uuid4,
    editable = False
  )
  order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
  product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
  quantity = models.PositiveIntegerField(default=1)
  price = models.DecimalField(max_digits=10, decimal_places=2)
  discount_percentage = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(100)])

  def __str__(self):
    return f"{self.quantity} x {self.product.name} - {self.subtotal()} for {self.order.user.username}"

  def subtotal(self):
    return  self.quantity * (self.price - ((self.price * self.discount_percentage) / 100))

  def save(self, *args, **kwargs):
    if not self.quantity:
      self.quantity = self.product.stock

    # ensure quantity doesn't exceed available stock
    if self.quantity > self.product.stock:
      self.quantity = self.product.stock

    super().save(*args, **kwargs)
