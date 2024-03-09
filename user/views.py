from django.urls import reverse_lazy
from django.shortcuts import redirect, reverse, render, get_object_or_404
from django.views.generic import TemplateView, DetailView, UpdateView, FormView, ListView, DeleteView, CreateView, View
from allauth.account.views import SignupView, LoginView, PasswordChangeView
from .forms import CustomerSignupForm, StoreSignupForm, ProfileForm, AddressAddForm, AddressUpdateForm
from django.contrib import messages
from .models import Profile, CustomUser, Address
from products.models import Product, Category
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from random import sample
from django.db.models import Q
from django.conf import settings
from allauth.account.forms import ChangePasswordForm
from django.http import HttpResponseRedirect, Http404

# permissions
class CustomerGroupRequiredMixin(UserPassesTestMixin):
  def test_func(self):
    return self.request.user.groups.filter(name='customer').exists()

class StoreGroupRequiredMixin(UserPassesTestMixin):
  def test_func(self):
    return self.request.user.groups.filter(name='store').exists()

# to allow access to customers and guests only not store
class CustomerGroupAndGuestRequiredMixin(UserPassesTestMixin):
  def test_func(self):
    user = self.request.user
    return not user.is_authenticated or user.groups.filter(name='customer').exists()

  # when user in store grooup tries to visit homepage redirect to store dashboard instead of homepage
  def handle_no_permission(self):
    user = self.request.user
    if user.is_authenticated and user.groups.filter(name='store').exists():
      return redirect('store_dashboard')
    else:
      if user.is_authenticated:
        return redirect('home')
      else:
        return redirect('register')


class HomePageView(CustomerGroupAndGuestRequiredMixin, ListView):
  model = Product
  context_object_name = 'product_list'
  template_name = 'homepage/home.html'

  def get_queryset(self):
    # retrieve products with stock greater than 0
    all_products = Product.objects.filter(stock__gt=0, is_deleted=False)  

    # randomize the all_products and get only 12 products
    top_picks = sample(list(all_products), min(12, all_products.count()))

    return top_picks

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)

    all_products = Product.objects.filter(stock__gt=0, is_deleted=False) 

    mobiles = self.get_sample_products('Mobile', 12)
    fashions = self.get_sample_products('Fashion', 9)
    beauties = self.get_sample_products('Beauty & Health', 9)
    liquors = self.get_sample_products('Liquor', 9)
    just_for_you = sample(list(all_products), min(13, all_products.count()))

    context['mobiles'] = mobiles
    context['fashions'] = fashions
    context['beauties'] = beauties
    context['liquors'] = liquors
    context['just_for_you'] = just_for_you

    # displaying images
    self.set_primary_image_urls(context['product_list'])
    self.set_primary_image_urls(context['mobiles'])
    self.set_primary_image_urls(context['fashions'])
    self.set_primary_image_urls(context['beauties'])
    self.set_primary_image_urls(context['liquors'])
    self.set_primary_image_urls(context['just_for_you'])

    return context

  # to reduce code repetency
  def get_sample_products(self, category_name, count):
    category = Category.objects.filter(name=category_name).first()
    all_products = Product.objects.filter(
      Q(category=category) | Q(category__parent=category) | Q(category__parent__parent=category),
      stock__gt=0, is_deleted=False
    )
    return sample(list(all_products), min(count, all_products.count()))

  def set_primary_image_urls(self, products):
    for product in products:
      if product.images.exists():
        product.primary_image_url = product.images.first().image.url
      else:
        product.primary_image_url = None


class RegisterPage(TemplateView):
  template_name = 'account/register.html'


# overriding default allauth signup view
class CustomerSignupView(SignupView):
  form_class = CustomerSignupForm
  success_url = reverse_lazy('home')
  
  def get(self, request, *args, **kwargs):
    return redirect(reverse('register'))

  def form_valid(self, form):
    response = super().form_valid(form)
    user = self.user

    if user:
      customer_group = Group.objects.get(name='customer')
      user.groups.add(customer_group)
    else:
      messages.error(self.request, "An error occurred during user registration.")
      return redirect(reverse('account_login'))
    return response

  # redirecting to register page on signup error
  def form_invalid(self, form):
    response = super().form_invalid(form)

    error_messages = [str(error) for error in form.errors.values()]
    for error_message in error_messages:
      messages.error(self.request, error_message)

    return redirect(reverse('register'))


class StoreSignupView(SignupView):
  form_class = StoreSignupForm
  template_name = 'store/signup.html'
  success_url = reverse_lazy('store_dashboard')

  def form_valid(self, form):
    response = super().form_valid(form)
    user = self.user

    if user:
      store_group = Group.objects.get(name='store')
      user.groups.add(store_group)
    else:
      messages.error(self.request, "An error occurred during user registration.")
      return redirect(reverse('store_signup'))
    
    return response

  def form_invalid(self, form):
    response = super().form_invalid(form)

    error_messages = [str(error) for error in form.errors.values()]
    for error_message in error_messages:
      messages.error(self.request, error_message)

    return response


# overriding default allauth login view
class CustomerLoginView(LoginView):
  def get(self, request, *args, **kwargs):
    next_url = request.GET.get('next')
    if next_url:
      # store the 'next' url in session
      request.session['next'] = next_url
    # redirecting to register page instead of default login page
    return redirect(reverse('register'))

  def form_valid(self, form):
    if form.is_valid():
      user = form.user
      if user is not None and user.groups.filter(name='customer').exists():
        if not user.is_active:
          messages.error(self.request, "Your account has been deleted.")
          return redirect(reverse('register'))
        login(self.request, user)
        next_url = self.request.session.get('next')
        if next_url:
          del self.request.session['next'] # remove next from session
          return redirect(next_url)
        else:
          return super().form_valid(form)
      else:
        messages.error(self.request, "You do not have permission to log in as a user.")
        return redirect(reverse('register'))
      
  # redirecting to register page on login error
  def form_invalid(self, form):
    response = super().form_invalid(form)

    error_messages = [str(error) for error in form.errors.values()]
    for error_message in error_messages:
      messages.error(self.request, error_message)

    return redirect(reverse('register'))


class StoreLoginView(LoginView):
  template_name = 'store/login.html'
  success_url = reverse_lazy('store_dashboard')

  def get(self, request, *args, **kwargs):
    next_url = request.GET.get('next')
    if next_url:
      request.session['next'] = next_url
    return super().get(request, *args, **kwargs)

  def form_valid(self, form):
    if form.is_valid():
      user = form.user
      if user is not None and user.groups.filter(name='store').exists():
        if not user.is_active:
          messages.error(self.request, "Your account has been deleted.")
          return redirect(reverse_lazy('store_signup'))
        login(self.request, user)
        next_url = self.request.session.get('next')
        if next_url:
          del self.request.session['next']
          return redirect(next_url)
        else:
          return super().form_valid(form)
      else:
        messages.error(self.request, "You do not have permission to log in as a store.")
        return redirect(reverse_lazy('store_login'))
      
  def form_invalid(self, form):
    response = super().form_invalid(form)

    error_messages = [str(error) for error in form.errors.values()]
    for error_message in error_messages:
      messages.error(self.request, error_message)

    return response


class BaseStoreDashboard(TemplateView):
  template_name = 'store/dashboard.html'

  def get_queryset(self):
    return Product.objects.filter(store=self.request.user, is_deleted=False)  
    
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['products'] = self.get_queryset()
 
    # displaying images
    for product in context['products']:
      if product.images.exists():
        product.primary_image_url = product.images.first().image.url
      else:
        product.primary_image_url = None

    return context


class StoreDashboard(LoginRequiredMixin, StoreGroupRequiredMixin, BaseStoreDashboard):
  pass

# for customer to view store's profile
class StoreProfileCustomerView(LoginRequiredMixin, BaseStoreDashboard):
  def get_queryset(self):
    store_pk = self.kwargs.get('pk')
    return Product.objects.filter(store_id=store_pk, is_deleted=False)

  # to pass info of store in template
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    store_pk = self.kwargs.get('pk')
    store = CustomUser.objects.get(pk=store_pk)
    context["store"] = store
    return context
  

class BaseProfileDetailView(LoginRequiredMixin, DetailView):
  model = Profile
  template_name = 'account/profile.html'
  context_object_name = 'profile'

  def get_object(self, queryset=None):
    return self.request.user.profile

  
class ProfileDetailView(BaseProfileDetailView):
  pass


# for store to view customers profile
class CustomerProfileStoreView(StoreGroupRequiredMixin, BaseProfileDetailView):
  template_name = 'account/customer_profile.html'

  def get_object(self, queryset=None):
    uuid = self.kwargs.get('pk')
    return Profile.objects.get(user_id=uuid)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
  model = Profile
  form_class = ProfileForm
  template_name = 'account/profile_update.html'
  success_url = '/profile/'

  def get_object(self, queryset=None):
    return self.request.user.profile

  # for excluding gender and birthdate fields for stores
  def get_form(self, form_class=None):
    form = super().get_form(form_class)
    form.fields.pop('email', None)
    if self.request.user.groups.filter(name='store').exists():
      form.fields.pop('gender', None)
      form.fields.pop('birth_date', None)
    return form

  def form_valid(self, form):
    messages.success(self.request, "Profile updated successfully.")
    return super().form_valid(form)

  def form_invalid(self, form):
    messages.error(self.request, "Please correct the errors below.")
    return super().form_invalid(form)
  

# override allauth password change view
class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
  success_url = reverse_lazy('home')

  def form_invalid(self, form):
    response = super().form_invalid(form)
    for field, errors in form.errors.items():
      for error in errors:
        messages.error(self.request, f'{field}: {error}')
    return response
  

class UserDeleteView(LoginRequiredMixin, DeleteView):
  model = CustomUser
  template_name = 'account/delete.html'
  success_url = reverse_lazy('home')

  def get_object(self, queryset=None):
    return self.request.user

  def post(self, request, *args, **kwargs):
    password = request.POST.get('password', '')
    user = self.get_object()
    if not authenticate(username=user.username, password=password):
      messages.error(request, 'Incorrect password')
      return HttpResponseRedirect(self.request.path_info) # path_info: attribute of HttpRequest which represents path of requested url
    
    try:
      self.object = user
      success_url = self.get_success_url()
      self.object.delete() # calls delete function in model
      logout(request)
      messages.success(request, 'Your account has been deleted successfully.')
      return HttpResponseRedirect(success_url)
    except Exception as e:
      messages.error(request, f'An error occured while deleting your account: {str(e)}')
      return HttpResponseRedirect(self.request.path_info)


class AddressListView(LoginRequiredMixin, CustomerGroupRequiredMixin, ListView):
  model = Address
  template_name = 'address/list.html'
  context_object_name = 'address_list'

  def get_queryset(self):
    user = self.request.user
    return Address.objects.filter(user=user)


class AddressAddView(LoginRequiredMixin, CustomerGroupRequiredMixin, CreateView):
  model = Address 
  form_class = AddressAddForm
  template_name = 'address/add.html'
  success_url = reverse_lazy('address_list')

  def form_valid(self, form):
    form.instance.user = self.request.user
    messages.success(self.request, 'Address added successfully!')
    return super().form_valid(form)

  def form_invalid(self, form):
    for field, errors in form.errors.items():
      for error in errors:
        messages.error(self.request, f"{field}: {error}")
    return super().form_invalid(form)


class AddressUpdateView(LoginRequiredMixin, CustomerGroupRequiredMixin, UpdateView):
  model = Address 
  form_class = AddressUpdateForm
  template_name = 'address/update.html'
  success_url = reverse_lazy('address_list')

  def dispatch(self, request, *args, **kwargs):
    self.object = self.get_object()

    if self.object.user != request.user:
      messages.error(request, "You are not authorized to update this product.")
      return HttpResponseRedirect(success_url)
    return super().dispatch(request, *args, **kwargs)

  def form_valid(self, form):
    messages.success(self.request, "Address updated successfully!")
    return super().form_valid(form)

  def form_invalid(self, form):
    for field, errors in form.errors.items():
      for error in errors:
        messages.error(self.request, f"{field}: {error}")
    return super().form_invalid(form)


class AddressDeleteView(LoginRequiredMixin, CustomerGroupRequiredMixin, View):
  model = Address
  success_url = reverse_lazy('address_list')

  def post(self, request, pk):
    try:
      address = get_object_or_404(Address, pk=pk)
      address.delete()
      messages.success(request, f"Your address was deleted successfully.")
    except Exception as e:
      messages.error(request, f"An error occurred while deleting address: {str(e)}")
    return redirect(self.success_url)
