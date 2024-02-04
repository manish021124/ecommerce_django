from django import forms
from allauth.account.forms import SignupForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

class CustomUserCreationForm(UserCreationForm):
  full_name = forms.CharField(max_length=50, label='Full Name', required=True)
  mobile = forms.CharField(max_length=10, label='Mobile', required=True)

  class Meta:
    model = get_user_model()
    fields = ('email', 'username', 'full_name', 'mobile')

  def save(self, request):
    user = super(CustomUserCreationForm, self).save(request)
    user.full_name = self.cleaned_data.get('full_name', '')
    user.mobile = self.cleaned_data.get('mobile', '')
    user.save()
    return user

class CustomUserChangeForm(UserChangeForm):
  full_name = forms.CharField(max_length=50, label='Full Name', required=True)
  mobile = forms.CharField(max_length=10, label='Mobile', required=True)

  class Meta:
    model = get_user_model()
    fields = ('email', 'username', 'full_name', 'mobile')

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.initial['full_name'] = f"{self.instance.first_name} {self.instance.last_name}".strip()

  def save(self, commit=True):
    user = super(CustomUserChangeForm, self).save(commit=False)
    user.full_name = self.cleaned_data.get('full_name', '')
    user.mobile = self.cleaned_data.get('mobile', '')
    
    if commit:
      user.save()
    return user

class CustomSignupForm(SignupForm):
  full_name = forms.CharField(max_length=50, label='Full Name', required=True)
  mobile = forms.CharField(max_length=10, label='Mobile', required=True)

  def save(self, request):
    user = super(CustomSignupForm, self).save(request)
    user.full_name = self.cleaned_data.get('full_name', '')
    user.mobile = self.cleaned_data.get('mobile', '')
    user.save()

    return user