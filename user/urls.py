from django.urls import include, path
from . import views
from .views import (
  HomePageView, 
  RegisterPage, 
  CustomerSignupView, 
  CustomerLoginView, 
  StoreSignupView, 
  StoreLoginView, 
  StoreDashboard, 
  ProfileDetailView, 
  ProfileUpdateView,
  StoreProfileCustomerView,
  CustomerProfileStoreView,
  CustomPasswordChangeView,
  UserDeleteView,
)

urlpatterns = [
  path('accounts/delete/<uuid:pk>/', UserDeleteView.as_view(), name='delete_account'),
  path('accounts/password/change/', CustomPasswordChangeView.as_view(), name='password_change'),
  path('profile/', ProfileDetailView.as_view(), name='profile_detail'),  
  path('profile/update/', ProfileUpdateView.as_view(), name='profile_update'),
  path('accounts/store/signup', StoreSignupView.as_view(), name='store_signup'),
  path('accounts/store/login', StoreLoginView.as_view(), name='store_login'),
  path('customer/<uuid:pk>/profile', CustomerProfileStoreView.as_view(), name='customer_profile_for_store'),
  path('store/<uuid:pk>/profile', StoreProfileCustomerView.as_view(), name='store_profile_for_customer'),
  path('store/dashboard', StoreDashboard.as_view(), name='store_dashboard'),
  path('accounts/signup/', CustomerSignupView.as_view(), name='account_signup'),  # overriding default allauth urls
  path('accounts/login/', CustomerLoginView.as_view(), name='account_login'),
  path('accounts/register/', RegisterPage.as_view(), name='register'),
  path('accounts/', include("allauth.urls")),
  path('', HomePageView.as_view(), name='home'),
]