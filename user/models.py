from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class CustomUser(AbstractUser):
  # custom signup form fields
  full_name = models.CharField(max_length=50, default='Default Name')
  mobile = models.CharField(max_length=10, blank=False, null=False)

  def save(self, *args, **kwargs):
    if not self.full_name:
      self.full_name = f"{self.first_name} {self.last_name}".strip() or self.username
    super().save(*args, **kwargs)

  def __str__(self):
    return self.username