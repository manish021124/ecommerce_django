from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, TemplateView, ListView
from .models import Product, Category
from .forms import ProductAddForm, ProductUpdateForm, ProductImageForm, ProductImageFormSet
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from user.views import StoreGroupRequiredMixin
from django.shortcuts import get_object_or_404
from random import shuffle
from django.db.models import Q

class ProductDetailView(DetailView):
  model = Product
  context_object_name = 'product'
  template_name = 'products\product_detail.html'
  

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

  # UpdateView does it so not needed
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
  success_url = reverse_lazy('store_dashboard')

  # let only the owner to delete product
  def dispatch(self, request, *args, **kwargs):
    self.object = self.get_object()

    # check if the current user is the owner of the product
    if self.object.store != request.user:
      messages.error(request, "You are not authorized to delete this product.")
      return HttpResponseRedirect(reverse('product_detail', kwargs={'pk': self.object.pk}))
    return super().dispatch(request, *args, **kwargs)

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    try:
      self.object.delete() # call delete() of product model
      messages.success(request, "Product deleted successfully.")
    except Exception as e:
      messages.error(request, f"An error occured while deleting the product: {str(e)}")
    return HttpResponseRedirect(success_url)


class ProductByCategoryView(TemplateView):
  template_name = 'products/category.html'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    category_name = self.kwargs['category']
    category = get_object_or_404(Category, name=category_name)
    queryset = Product.objects.filter(
      Q(category=category) | Q(category__parent=category) | Q(category__parent__parent=category),
      stock__gt=0,
      is_deleted=False
    )

    user = self.request.user
    if user.groups.filter(name='store').exists():
      queryset = queryset.filter(store=user)
    # get all products and suffle them
    products = list(queryset)
    shuffle(products)
    total_products = len(products)
    context["products"] = products
    context["category_totals"] = {category_name: total_products}

    for product in context["products"]:
      if product.images.exists():
        product.primary_image_url = product.images.first().image.url
      else:
        product.primary_image_url = None

    return context


class SearchResultsView(ListView):
  template_name = 'search_results.html'
  context_object_name = 'results'

  def get_queryset(self):
    query = self.request.GET.get('query', '')
    products = Product.objects.filter(
        Q(name__icontains=query) |  # icontains is a lookup filter in django's orm system
        Q(category__name__icontains=query),
        is_deleted=False
      )
    if self.request.user.groups.filter(name='store').exists():
      products = products.filter(store=self.request.user)
    else:
      products = products.filter(stock__gt=0)

    return products

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['query'] = self.request.GET.get('query', '')
    return context

  