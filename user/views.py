from django.urls import reverse_lazy
from django.shortcuts import redirect, reverse, render
from django.views.generic import TemplateView
from allauth.account.views import SignupView, LoginView
from .forms import CustomSignupForm
from django.contrib import messages
from django.views.generic import ListView
from products.models import Product, Category

# Create your views here.
class HomePageView(ListView):
  model = Product
  context_object_name = 'product_list'
  template_name = 'home.html'

  def get_queryset(self):
    # retrieve products with stock greater than 0
    return Product.objects.filter(stock__gt=0)  

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
class CustomSignupView(SignupView):
  form_class = CustomSignupForm
  success_url = reverse_lazy('home')
  
  # redirecting to register page instead of default signup page
  def get(self, request, *args, **kwargs):
    return redirect(reverse('register'))

  def form_valid(self, form):
    response = super().form_valid(form)
    return response

  # redirecting to register page on signup error
  def form_invalid(self, form):
    response = super().form_invalid(form)

    # pass default allauth or django error message to redirected page
    error_messages = [str(error) for error in form.errors.values()]
    for error_message in error_messages:
      messages.error(self.request, error_message)

    return redirect(reverse('register'))
    

# overriding default allauth login view
class CustomLoginView(LoginView):
  # redirecting to register page instead of default login page
  def get(self, request, *args, **kwargs):
    next_url = request.GET.get('next')
    if next_url:
      # store the 'next' url in session
      request.session['next'] = next_url
    return redirect(reverse('register'))

  def form_valid(self, form):
    response = super().form_valid(form)
    # after login redirect to the 'next' url if available
    next_url = self.request.session.get('next')
    if next_url:
      del self.request.session['next'] #remove 'next' url from session
      return redirect(next_url)
    else:
      return response

  # redirecting to register page on login error
  def form_invalid(self, form):
    response = super().form_invalid(form)

    error_messages = [str(error) for error in form.errors.values()]
    for error_message in error_messages:
      messages.error(self.request, error_message)

    return redirect(reverse('register'))
  