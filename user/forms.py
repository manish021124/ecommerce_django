from django import forms
from .models import CustomUser, Profile, Address
from allauth.account.forms import SignupForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

#updates user addition form in admin panel
class CustomUserCreationForm(UserCreationForm):
  full_name = forms.CharField(max_length=50, label='Full Name', required=True)
  mobile = forms.CharField(max_length=10, label='Mobile', required=True)

  class Meta:
    model = get_user_model()
    fields = ('email', 'username', 'full_name', 'mobile')

  def save(self, commit=True):
    user = super().save(commit=False)
    user.full_name = self.cleaned_data.get('full_name', '')
    user.mobile = self.cleaned_data.get('mobile', '')
    if commit:
      user.save()
    return user


#to allow admin to modify details and to include additional fields in user edit form
class CustomUserChangeForm(UserChangeForm):
  full_name = forms.CharField(max_length=50, label='Full Name', required=True)
  mobile = forms.CharField(max_length=10, label='Mobile', required=True)

  class Meta:
    model = get_user_model()
    fields = ('email', 'username', 'full_name', 'mobile')

  def save(self, commit=True):
    user = super().save(commit=False)
    user.full_name = self.cleaned_data.get('full_name', '')
    user.mobile = self.cleaned_data.get('mobile', '')
    
    if commit:
      user.save()
    return user
    

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

  def clean_email(self):
    email = self.cleaned_data.get('email')
    if email and CustomUser.objects.filter(email=email).exists():
      user = CustomUser.objects.get(email=email)
      if not user.is_active:
        raise forms.ValidationError("This email has been already used and cannot be registered again.")
      else:
        raise forms.ValidationError("This email is already registered. Please Login instead.")
    return email


class CustomerSignupForm(BaseSignupForm):
  pass


class StoreSignupForm(BaseSignupForm):
  pass


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
      self.fields['full_name'].initial = self.instance.user.full_name
      self.fields['mobile'].initial = self.instance.user.mobile

  def save(self, commit=True):
    profile = super(ProfileForm, self).save(commit=False)
    if self.instance and self.instance.user:
      user = self.instance.user
      user.username = self.cleaned_data['username']
      user.full_name = self.cleaned_data['full_name']
      user.mobile = self.cleaned_data['mobile']
      if commit:
        profile.save()
        user.save()
    return profile


class BaseAddressForm(forms.ModelForm):
  class Meta:
    model = Address
    fields = ['province', 'city', 'area', 'tole']
  
  def save(self, commit=True):
    address = super().save(commit=commit)
    return address


class AddressAddForm(BaseAddressForm):
  pass


class AddressUpdateForm(BaseAddressForm):
  pass


# for adding address while placing order
class AddressRadioForm(forms.ModelForm):
  class Meta:
    model = Address
    fields = ['province', 'city', 'area', 'tole']