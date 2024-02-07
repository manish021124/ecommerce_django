from django.shortcuts import render
from django.views.generic import ListView, DetailView 
from .models import Product


class ProductDetailView(DetailView):
  model = Product
  context_object_name = 'product'
  template_name = 'products\product_detail.html'