import uuid
from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from products.models import Product
from django.utils.timezone import now
from django.utils.crypto import get_random_string
from django.db.models import F, Sum, ExpressionWrapper, DecimalField
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

  # ensures order_number is populated with unique order number
  def save(self, *args, **kwargs):
    if not self.order_number:
      self.order_number = uuid.uuid4().hex[:10].upper()

    self.total_amount = self.calculate_total_amount()

    super().save(*args, **kwargs)

  def calculate_total_amount(self):
    cart_items = self.user.cart.items.all()
    aggregation_result = cart_items.aggregate(
      total_amount = Sum(
        ExpressionWrapper(
          F('quantity') * (F('price') - (F('price') * F('discount_percentage') / 100)),
          output_field = DecimalField()
        )
      )
    )
    total_amount = aggregation_result.get('total_amount')
    return total_amount if total_amount is not None else 0
  

class OrderItem(models.Model):
  id = models.UUIDField(
    primary_key = True,
    default = uuid.uuid4,
    editable = False
  )
  order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
  product = models.ForeignKey(Product, on_delete=models.PROTECT)
  quantity = models.PositiveIntegerField(default=1)
  price = models.DecimalField(max_digits=10, decimal_places=2)
  discount_percentage = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(100)])

  def __str__(self):
    return f"{self.quantity} x {self.product} - {self.subtotal()} for {self.order.user.username}"

  def subtotal(self):
    return self.quantity * (self.price - ((self.price * self.discount_percentage) / 100))
