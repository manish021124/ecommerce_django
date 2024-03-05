from django.urls import path
from .views import (
  ProductDetailView, 
  ProductCreateView, 
  ProductUpdateView, 
  ProductDeleteView, 
  ProductByCategoryView
)
from user.views import HomePageView

urlpatterns = [
  path('', HomePageView.as_view(), name='products'),
  path('<uuid:pk>', ProductDetailView.as_view(), name='product_detail'),
  path('add/', ProductCreateView.as_view(), name='product_add'),
  path('update/<uuid:pk>/', ProductUpdateView.as_view(), name='product_update'),
  path('<uuid:pk>/delete', ProductDeleteView.as_view(), name='product_delete'),
  path('<str:category>', ProductByCategoryView.as_view(), name='product_by_category'),
]
