import uuid
from django.contrib.auth.models import AbstractUser, Permission
from django.db import models
from django.conf import settings 
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator

class CustomUser(AbstractUser):
  id = models.UUIDField(
    primary_key = True,
    default = uuid.uuid4,
    editable = False
  )
  # custom fields
  full_name = models.CharField(max_length=50, default='Default Name')
  mobile = models.CharField(max_length=10, blank=False, null=False)

  def __str__(self):
    return self.username

  # override default delete function
  def delete(self, using=None, keep_parents=False):
    self.is_active = False
    self.save()
    self.manage_deletion() # cancel orders associated with user

  def manage_deletion(self):
    from orders.models import Order # shows error when import outside function
    from products.models import Product
    from carts.models import Cart

    if self.groups.filter(name='store').exists():
      products_to_delete = Product.objects.filter(store=self)
      products_to_delete.update(is_deleted=True) # set product is_deleted true, don't need to iterate cause of update() being used
      orders_to_cancel = Order.objects.filter(items__product__in=products_to_delete, status__in=['Pending', 'Processing'])
      for order in orders_to_cancel:
        order.status = 'Cancelled' # set order status to cancelled if exist in pending and processing status while deleting store account
        order.save()
      carts_to_modify = Cart.objects.filter(items__product__in=products_to_delete)
      for cart in carts_to_modify:
        cart.items.filter(product__in=products_to_delete).delete()
        if cart.items.count() == 0:
          cart.delete()
    else:
      orders_to_cancel = Order.objects.filter(user=self, status__in=['Pending', 'Processing'])
      for order in orders_to_cancel:
        order.status = 'Cancelled' # set order status to cancelled if exist in pending and processing status while deleting customer account
        order.save()
      try:
        user_cart = Cart.objects.get(user=self)
        user_cart.delete()
      except Cart.DoesNotExist:
        pass


#no need to use signals.py
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
  if created:
    Profile.objects.create(user=instance)
  else:
    instance.profile.save()    


class Profile(models.Model):
  GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
  )
  user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  birth_date = models.DateField(null=True, blank=True)
  gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)

  def __str__(self):
    return self.user.username + "'s Profile"


class Address(models.Model):
  PROVINCE_CHOICES = (
    ('Province 1', 'Koshi Province'),
    ('Province 2', 'Madesh Province'),
    ('Province 3', 'Bagmati Province'),
    ('Province 4', 'Gandaki Province'),
    ('Province 5', 'Lumbini Province'),
    ('Province 6', 'Karnali Province'),
    ('Province 7', 'Sudurpashchim Province'),
  )
  id = models.UUIDField(
    primary_key = True,
    default = uuid.uuid4,
    editable = False
  )
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'groups__name': 'customer'})
  province = models.CharField(max_length=100, choices=PROVINCE_CHOICES)
  city = models.CharField(max_length=100)
  area = models.CharField(max_length=100)
  tole = models.IntegerField(validators=[MinValueValidator(0)])

  def __str__(self):
    return self.user.username + "'s Address"