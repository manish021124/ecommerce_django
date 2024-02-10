from django.urls import path
from .views import ProductDetailView
from user.views import HomePageView

urlpatterns = [
  path('', HomePageView.as_view(), name='products'),
  path('<uuid:pk>', ProductDetailView.as_view(), name='product_detail'),
]
