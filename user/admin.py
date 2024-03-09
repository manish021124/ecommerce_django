from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import Profile, Address
from .forms import CustomUserCreationForm, CustomUserChangeForm

CustomUser = get_user_model()

class CustomUserAdmin(UserAdmin):
  add_form = CustomUserCreationForm
  form = CustomUserChangeForm
  model = CustomUser
  list_display = ['email', 'full_name', 'mobile', 'get_groups', 'is_superuser', 'is_active',]

  def get_groups(self, obj):
    return ", ".join([group.name for group in obj.groups.all()])
  get_groups.short_description = 'Groups' # sets colunm header
 
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
admin.site.register(Address)