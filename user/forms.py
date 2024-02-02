from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class CustomUserCreationForm(UserCreationForm):
  # name = forms.CharField(max_length = 40)
  # mobile = forms.CharField(max_length = 10)
  # email = forms.EmailField()

  class Meta:
    model = get_user_model()
    fields = ('email', 'username',)

class CustomUserChangeForm(UserChangeForm):
  class Meta:
    model = get_user_model()
    fields = ('email', 'username',)
