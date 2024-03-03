from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from .models import Product, Category
from .forms import ProductAddForm, ProductUpdateForm, ProductImageForm, ProductImageFormSet
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
    context['store'] = self.object.store
    return context
  

class ProductCreateView(LoginRequiredMixin, StoreGroupRequiredMixin, CreateView):
  model = Product
  form_class = ProductAddForm
  template_name = 'products/add.html'

  # Override get_context_data to include form and image_formset in context
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    if self.request.POST:
      # If form is submitted with POST data, populate form and image_formset with POST data
      context['form'] = self.form_class(self.request.POST, self.request.FILES)
      context['image_formset'] = ProductImageFormSet(self.request.POST, self.request.FILES)
    else:
      # If no POST data, provide empty form and image_formset
      context['form'] = self.form_class()
      context['image_formset'] = ProductImageFormSet()
    return context

  # Override form_valid to save form and image_formset data if both are valid
  def form_valid(self, form):
    context = self.get_context_data()
    image_formset = context['image_formset']
    if form.is_valid() and image_formset.is_valid():
      # Save the product form
      self.object = form.save(commit=False)
      self.object.store = self.request.user
      self.object.save()
      # Associate the image_formset with the newly created product and save it
      image_formset.instance = self.object
      image_formset.save()
      messages.success(self.request, 'Product added successfully!')
      return super().form_valid(form)
    else:
      return self.form_invalid(form)

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
    try:
      return Product.objects.get(pk=self.kwargs['pk'])
    except Product.DoesNotExist:
      raise Http404("Product does not exist")

  # let only the owner to update product
  def dispatch(self, request, *args, **kwargs):
    self.object = self.get_object()

    # check if the current user is the owner of the product
    if self.object.store != request.user:
      messages.error(request, "You are not authorized to update this product.")
      return HttpResponseRedirect(self.get_success_url())
    return super().dispatch(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    if self.request.POST:
      context['form'] = self.form_class(self.request.POST, instance=self.object)
      context['image_formset'] = ProductImageFormSet(self.request.POST, self.request.FILES, instance=self.object)
    else:
      context['form'] = self.form_class(instance=self.object)
      context['image_formset'] = ProductImageFormSet(instance=self.object)
    return context

  def form_valid(self, form):
    context = self.get_context_data()
    image_formset = context['image_formset']
    if form.is_valid() and image_formset.is_valid():
      self.object = form.save()
      image_formset.save()
      messages.success(self.request, 'Product updated successfully!')
      return super().form_valid(form)
    else:
      return self.form_invalid(form)
  
  def form_invalid(self, form):
    error_messages = []
    for field, errors in form.errors.items():
      for error in errors:
        error_messages.append(f"{field}: {error}")

    context = self.get_context_data()
    if 'image_formset' in context:
      for image_form in context['image_formset']:
        for field, errors in image_form.errors.items():
          for error in errors:
            error_messages.append(f"Image {field}: {error}")
    messages.error(self.request, "\n".join(error_messages))
    return super().form_invalid(form)
  

# can use view instead of deleteview to make it shorter and easier
class ProductDeleteView(LoginRequiredMixin, StoreGroupRequiredMixin, DeleteView):
  model = Product
  template_name = 'products/delete.html'

  def get_success_url(self):
    store_pk = self.object.store.pk
    return reverse_lazy('store_dashboard', kwargs={'pk': store_pk})

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
    success_url = self.get_success_url()
    self.object.is_deleted = True
    self.object.save()
    messages.success(request, "Product deleted successfully.")
    return HttpResponseRedirect(success_url)