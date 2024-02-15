from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import Profile
from .forms import CustomUserCreationForm, CustomUserChangeForm

# Register your models here.
CustomUser = get_user_model()

class CustomUserAdmin(UserAdmin):
  add_form = CustomUserCreationForm
  form = CustomUserChangeForm
  model = CustomUser
  list_display = ['email', 'full_name', 'mobile', 'is_staff', 'is_superuser',]
 
  # fields to be allowed to edit in admin panel
  fieldsets = (
    (None, {
      "fields": (
        'username', 'email', 'password'
      ),
    }),
    ('Personal info', {
      "fields": (
        'full_name', 'mobile'
      )
    }),
    ('Permissions', {
      "fields": (
        'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'
      ),
    }),
    ('Important dates', {
      "fields": (
        'last_login', 'date_joined'
      ),
    }),
  )
  

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Profile)