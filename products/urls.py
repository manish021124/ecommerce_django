from django.urls import path
from .views import (
  ProductDetailView, 
  ProductCreateView, 
  ProductUpdateView, 
  ProductDeleteView, 
  ProductByCategoryView,
  SearchResultsView,
  ReviewAddView,
  ReviewUpdateView,
  ReviewDeleteView,
)
from user.views import HomePageView

urlpatterns = [
  path('', HomePageView.as_view(), name='products'),
  path('<uuid:pk>', ProductDetailView.as_view(), name='product_detail'),
  path('add/', ProductCreateView.as_view(), name='product_add'),
  path('update/<uuid:pk>/', ProductUpdateView.as_view(), name='product_update'),
  path('<uuid:pk>/delete', ProductDeleteView.as_view(), name='product_delete'),
  path('<str:category>', ProductByCategoryView.as_view(), name='product_by_category'),
  path('search/results/', SearchResultsView.as_view(), name='search_results'),
  path('review/add/<uuid:order_item_id>/', ReviewAddView.as_view(), name='review_add'),
  path('review/update/<int:review_id>/', ReviewUpdateView.as_view(), name='review_update'),
  path('review/delete/<int:review_id>/', ReviewDeleteView.as_view(), name='review_delete'),
]
