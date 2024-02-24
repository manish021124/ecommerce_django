from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from .models import Product, Category
from .forms import ProductAddForm, ProductUpdateForm
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from user.views import StoreGroupRequiredMixin


class ProductDetailView(DetailView):
  model = Product
  context_object_name = 'product'
  template_name = 'products\product_detail.html'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["is_store_user"] = self.request.user.groups.filter(name='store').exists()
    return context
  

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

  # let only the owner to update product
  def dispatch(self, request, *args, **kwargs):
    self.object = self.get_object()

    # check if the current user is the owner of the product
    if self.object.store != request.user:
      messages.error(request, "You are not authorized to update this product.")
      return HttpResponseRedirect(self.get_success_url())
    return super().dispatch(request, *args, **kwargs)

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
  

class ProductDeleteView(LoginRequiredMixin, StoreGroupRequiredMixin, DeleteView):
  model = Product
  template_name = 'products/delete.html'
  success_url = reverse_lazy('products')

   # let only the owner to delete product
  def dispatch(self, request, *args, **kwargs):
    self.object = self.get_object()

    # check if the current user is the owner of the product
    if self.object.store != request.user:
      messages.error(request, "You are not authorized to delete this product.")
      return HttpResponseRedirect(self.get_success_url())
    return super().dispatch(request, *args, **kwargs)

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    self.object.is_deleted = True
    self.object.save()
    messages.success(request, "Product deleted successfully.")
    return HttpResponseRedirect(self.get_success_url())

  def get_success_url(self):
    return reverse('products')