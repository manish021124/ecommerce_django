from django import forms
from .models import CustomUser, Profile
from allauth.account.forms import SignupForm
from django.contrib.auth import get_user_model
# from django.contrib.auth.forms import UserCreationForm, UserChangeForm

#updates user addition form in admin panel
# class CustomUserCreationForm(UserCreationForm):
#   full_name = forms.CharField(max_length=50, label='Full Name', required=True)
#   mobile = forms.CharField(max_length=10, label='Mobile', required=True)

#   class Meta:
#     model = get_user_model()
#     fields = ('email', 'username', 'full_name', 'mobile')

#   def save(self, commit=True):
#     user = super(CustomUserCreationForm, self).save(commit=False)
#     user.full_name = self.cleaned_data.get('full_name', '')
#     user.mobile = self.cleaned_data.get('mobile', '')
#     if commit:
#       user.save()
#     return user


# #to allow admin to modify details and to include additional fields in user edit form
# class CustomUserChangeForm(UserChangeForm):
#   full_name = forms.CharField(max_length=50, label='Full Name', required=True)
#   mobile = forms.CharField(max_length=10, label='Mobile', required=True)

#   class Meta:
#     model = get_user_model()
#     fields = ('email', 'username', 'full_name', 'mobile')

#   def save(self, commit=True):
#     user = super(CustomUserChangeForm, self).save(commit=False)
#     user.full_name = self.cleaned_data.get('full_name', '')
#     user.mobile = self.cleaned_data.get('mobile', '')
    
#     if commit:
#       user.save()
#     return user
    

# for adding custom fields in signup form using allauth
class BaseSignupForm(SignupForm):
  full_name = forms.CharField(max_length=50, label='Full Name', required=True)
  mobile = forms.CharField(max_length=10, label='Mobile', required=True)

  def save(self, request):
    user = super().save(request)
    user.full_name = self.cleaned_data.get('full_name', '')
    user.mobile = self.cleaned_data.get('mobile', '')
    user.save()
    return user


class CustomerSignupForm(BaseSignupForm):
  pass


class StoreSignupForm(BaseSignupForm):
  pass


# class CustomLoginForm(LoginForm):
#   def get_user(self):
#     return self.user_cache


class ProfileForm(forms.ModelForm):
  username = forms.CharField(max_length=255)
  email = forms.EmailField()
  full_name = forms.CharField(max_length=255)
  mobile = forms.CharField(max_length=10)

  class Meta:
    model = Profile
    fields = ['username', 'email', 'full_name', 'mobile', 'birth_date', 'gender']

  def __init__(self, *args, **kwargs):
    super(ProfileForm, self).__init__(*args, **kwargs)
    if self.instance and self.instance.user:
      self.fields['username'].initial = self.instance.user.username
      self.fields['email'].initial = self.instance.user.email
      self.fields['full_name'].initial = self.instance.user.full_name
      self.fields['mobile'].initial = self.instance.user.mobile

  def save(self, commit=True):
    profile = super(ProfileForm, self).save(commit=False)
    if self.instance and self.instance.user:
      user = self.instance.user
      user.username = self.cleaned_data['username']
      user.email = self.cleaned_data['email']
      user.full_name = self.cleaned_data['full_name']
      user.mobile = self.cleaned_data['mobile']
      if commit:
        profile.save()
        user.save()
    return profile