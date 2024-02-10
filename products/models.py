import uuid
from django.db import models
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator

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

  def __str__(self):
    return self.name

  # for setting canonical url 
  def get_absolute_url(self):
    return reverse('product_detail', args=[str(self.id)])
  

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
  