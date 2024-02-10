from django.shortcuts import render
from django.views.generic import DetailView
from .models import Product, Category


class ProductDetailView(DetailView):
  model = Product
  context_object_name = 'product'
  template_name = 'products\product_detail.html'