# from django.urls import reverse_lazy
# from django.views import generic
from django.shortcuts import render
from django.views.generic import TemplateView

# from .forms import CustomUserCreationForm

# Create your views here.
class HomePageView(TemplateView):
  template_name = 'home.html'

class CustomRegisterPage(TemplateView):
  template_name = 'register.html'

# class SignupPageView(generic.CreateView):
#   form_class = CustomUserCreationForm
#   success_url = reverse_lazy('account_login')
#   template_name = 'registration/signup.html'