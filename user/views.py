from django.urls import reverse_lazy
from django.shortcuts import redirect, reverse, render
from django.views.generic import TemplateView, DetailView, UpdateView, FormView
from allauth.account.views import SignupView, LoginView
from .forms import CustomerSignupForm, StoreSignupForm, ProfileForm
from django.contrib import messages
from django.views.generic import ListView
from .models import Profile
from products.models import Product, Category
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group

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


class HomePageView(CustomerGroupAndGuestRequiredMixin, ListView):
  model = Product
  context_object_name = 'product_list'
  template_name = 'home.html'

  def get_queryset(self):
    # retrieve products with stock greater than 0
    return Product.objects.filter(stock__gt=0, is_deleted=False)  

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
 
    # displaying images
    for product in context['product_list']:
      if product.images.exists():
        product.primary_image_url = product.images.first().image.url
      else:
        product.primary_image_url = None

    return context


class RegisterPage(TemplateView):
  template_name = 'register.html'


# overriding default allauth signup view
class CustomerSignupView(SignupView):
  form_class = CustomerSignupForm
  success_url = reverse_lazy('home')
  
  def get(self, request, *args, **kwargs):
    return redirect(reverse('register'))

  def form_valid(self, form):
    response = super().form_valid(form)
    user = self.user

    customer_group = Group.objects.get(name='customer')
    user.groups.add(customer_group)
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

    store_group = Group.objects.get(name='store')
    user.groups.add(store_group)
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


class StoreDashboard(LoginRequiredMixin, StoreGroupRequiredMixin, TemplateView):
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

  
class ProfileDetailView(LoginRequiredMixin, DetailView):
  model = Profile
  template_name = 'profile.html'
  context_object_name = 'profile'

  def get_object(self, queryset=None):
    return self.request.user.profile


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
  model = Profile
  form_class = ProfileForm
  template_name = 'profile_update.html'
  success_url = '/profile/'

  def get_object(self, queryset=None):
    return self.request.user.profile

  # for excluding gender and birthdate fields for stores
  def get_form(self, form_class=None):
    form = super().get_form(form_class)
    if self.request.user.groups.filter(name='store').exists():
      form.fields.pop('gender', None)
      form.fields.pop('birth_date', None)
    return form
  