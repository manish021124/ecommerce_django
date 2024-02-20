from django.shortcuts import render
from django.views.generic import DetailView
from .models import Product, Category
from django.views.generic.edit import CreateView 
from .forms import ProductAddForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin

class StoreGroupRequiredMixin(UserPassesTestMixin):
  def test_func(self):
    return self.request.user.groups.filter(name='store').exists()


class ProductDetailView(DetailView):
  model = Product
  context_object_name = 'product'
  template_name = 'products\product_detail.html'


class ProductCreateView(StoreGroupRequiredMixin, CreateView):
  model = Product
  form_class = ProductAddForm
  template_name = 'products/product_add_form.html'

  def form_valid(self, form):
    form.instance.store = self.request.user
    return super().form_valid(form)
  
  def get_success_url(self):
    return reverse_lazy('product_detail', kwargs={'pk': self.object.pk})
  