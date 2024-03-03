from django.urls import include, path
from . import views
from .views import HomePageView, RegisterPage, CustomerSignupView, CustomerLoginView, StoreSignupView, StoreLoginView, StoreDashboard, ProfileDetailView, ProfileUpdateView

urlpatterns = [
  path('profile/', ProfileDetailView.as_view(), name='profile_detail'),  
  path('profile/update/', ProfileUpdateView.as_view(), name='profile_update'),
  path('accounts/store/signup', StoreSignupView.as_view(), name='store_signup'),
  path('accounts/store/login', StoreLoginView.as_view(), name='store_login'),
  path('store/<uuid:pk>/dashboard', StoreDashboard.as_view(), name='store_dashboard'),
  path('accounts/signup/', CustomerSignupView.as_view(), name='account_signup'),  # overriding default allauth urls
  path('accounts/login/', CustomerLoginView.as_view(), name='account_login'),
  path('accounts/register/', RegisterPage.as_view(), name='register'),
  path('accounts/', include("allauth.urls")),
  path('', HomePageView.as_view(), name='home'),
]