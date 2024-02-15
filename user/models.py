import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings 
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class CustomUser(AbstractUser):
  id = models.UUIDField(
    primary_key = True,
    default = uuid.uuid4,
    editable = False
  )
  # custom signup form fields
  full_name = models.CharField(max_length=50, default='Default Name')
  mobile = models.CharField(max_length=10, blank=False, null=False)

  def save(self, *args, **kwargs):
    if not self.full_name:
      self.full_name = f"{self.first_name} {self.last_name}".strip() or self.username
    super().save(*args, **kwargs)

  def __str__(self):
    return self.username


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