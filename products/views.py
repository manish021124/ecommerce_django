from django.shortcuts import render
from django.views.generic import ListView, DetailView 
from .models import Product

# Create your views here.
class ProductListView(ListView):
  model = Product
  context_object_name = 'product_list'
  template_name = 'products\product_list.html'


class ProductDetailView(DetailView):
  model = Product
  context_object_name = 'product'
  template_name = 'products\product_detail.html'