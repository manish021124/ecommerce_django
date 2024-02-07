from django.urls import path
from .views import ProductDetailView

urlpatterns = [
  path('<uuid:pk>', ProductDetailView.as_view(), name='product_detail'),
]
