from django.shortcuts import render
from django.views.generic import DetailView, CreateView, UpdateView
from .models import Product, Category
from .forms import ProductAddForm, ProductUpdateForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


class StoreGroupRequiredMixin(UserPassesTestMixin):
  def test_func(self):
    return self.request.user.groups.filter(name='store').exists()


class ProductDetailView(DetailView):
  model = Product
  context_object_name = 'product'
  template_name = 'products\product_detail.html'


class ProductCreateView(LoginRequiredMixin, StoreGroupRequiredMixin, CreateView):
  model = Product
  form_class = ProductAddForm
  template_name = 'products/add.html'

  def form_valid(self, form):
    form.instance.store = self.request.user
    messages.success(self.request, 'Product added successfully!')
    return super().form_valid(form)

  def form_invalid(self, form):
    # get error messages from the form and add them to messages framework
    error_messages = []
    for field, errors in form.errors.items():
      for error in errors:
        error_messages.append(f"{field}: {error}")
    messages.error(self.request, "\n".join(error_messages))
    return super().form_invalid(form)
  
  def get_success_url(self):
    return reverse_lazy('product_detail', kwargs={'pk': self.object.pk})


class ProductUpdateView(LoginRequiredMixin, StoreGroupRequiredMixin, UpdateView):
  model = Product
  form_class = ProductUpdateForm
  template_name = 'products/update.html'

  def get_success_url(self):
    return reverse_lazy('product_detail', kwargs={'pk': self.object.pk})

  def get_object(self, queryset=None):
    return Product.objects.get(pk=self.kwargs['pk'])

  def form_valid(self, form):
    form.save()
    messages.success(self.request, 'Product updated successfully!')
    return super().form_valid(form)
  
  def form_invalid(self, form):
    error_messages = []
    for field, errors in form.errors.items():
      for error in errors:
        error_messages.append(f"{field}: {error}")
    messages.error(self.request, "\n".join(error_messages))
    return super().form_invalid(form)
  