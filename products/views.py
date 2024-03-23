from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, TemplateView, ListView
from .models import Product, Category, Review
from .forms import ProductAddForm, ProductUpdateForm, ProductImageForm, ProductImageFormSet, ReviewAddForm, ReviewUpdateForm
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from user.views import StoreGroupRequiredMixin, CustomerGroupRequiredMixin
from django.shortcuts import get_object_or_404
from random import shuffle
from django.db.models import Q
from orders.models import OrderItem

class ProductDetailView(DetailView):
  model = Product
  context_object_name = 'product'
  template_name = 'products/product_detail.html'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    product = self.get_object()
    reviews = Review.objects.filter(order_item__product=product).order_by('-created_at') # '-' for descending order
    rating_range = range(1, 6)
    
    if product.images.exists():
      product.primary_image_url = product.images.first().image.url
    else:
      product.primary_image_url = None

    context['reviews'] = reviews
    context['primary_image'] = product.primary_image_url
    context['rating_range'] = rating_range
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

  
class ReviewAddView(LoginRequiredMixin, CustomerGroupRequiredMixin, CreateView):
  model = Review
  form_class = ReviewAddForm
  template_name = 'reviews/add.html'

  def dispatch(self, request, *args, **kwargs):
    order_item_id = kwargs.get('order_item_id')
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    if request.user != order_item.order.user:
      messages.error(request, 'You are not authorized to add a review for this order item.')
      return redirect('home')
    return super().dispatch(request, *args, **kwargs)

  def get_form_kwargs(self):
    kwargs = super().get_form_kwargs()    
    order_item_id = self.kwargs.get('order_item_id')
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    kwargs['order_item'] = order_item
    return kwargs

  def form_valid(self, form):
    form.instance.user = self.request.user
    messages.success(self.request, 'Review added successfully!')
    return super().form_valid(form)

  def form_invalid(self, form):
    error_messages = []
    for field, errors in form.errors.items():
      for error in errors:
        error_messages.append(f"{field}: {error}")
    messages.error(self.request, "\n".join(error_messages))
    return super().form_invalid(form)
      
  def get_success_url(self):
    return reverse_lazy('product_detail', kwargs={'pk': self.object.order_item.product.id})


class ReviewUpdateView(LoginRequiredMixin, CustomerGroupRequiredMixin, UpdateView):
  model = Review
  template_name = 'reviews/edit.html'
  form_class = ReviewUpdateForm
  pk_url_kwarg = 'review_id' # override django's generic views identifier

  def dispatch(self, request, *args, **kwargs):
    self.object = self.get_object()
    if request.user != self.object.user:
      messages.error(request, 'You are not authorized to edit this review.')
      return HttpResponseRedirect(self.get_success_url())
    return super().dispatch(request, *args, **kwargs)

  def form_valid(self, form):
    form.instance.user = self.request.user
    messages.success(self.request, 'Review updated successfully!')
    return super().form_valid(form)

  def form_invalid(self, form):
    error_messages = []
    for field, errors in form.errors.items():
      for error in errors:
        error_messages.append(f"{field}: {error}")
    messages.error(self.request, "\n".join(error_messages))
    return super().form_invalid(form)

  def get_success_url(self):
    return reverse_lazy('product_detail', kwargs={'pk': self.object.order_item.product.id})


class ReviewDeleteView(LoginRequiredMixin, CustomerGroupRequiredMixin, DeleteView):
  model = Review
  template_name = 'reviews/delete.html'
  pk_url_kwarg = 'review_id'

  def dispatch(self, request, *args, **kwargs):
    self.object = self.get_object()
    if request.user != self.object.user:
      messages.error(request, 'You are not authorized to delete this review.')
      return HttpResponseRedirect(reverse('product_detail', kwargs={'pk': self.object.order_item.product.id}))
    return super().dispatch(request, *args, **kwargs)

  def delete(self, request, *args, **kwargs):
    response = super().delete(request, *args, **kwargs)
    if response.status_code == 302:
      messages.success(request, 'Review deleted successfully!')
    return response

  def get_success_url(self):
    return reverse_lazy('product_detail', kwargs={'pk': self.object.order_item.product.id})
