from django.urls import include, path
from . import views
from .views import HomePageView, RegisterPage, CustomSignupView, CustomLoginView, StoreSignupView, StoreDashboard, ProfileDetailView, ProfileUpdateView

urlpatterns = [
  path('profile/', ProfileDetailView.as_view(), name='profile_detail'),  
  path('profile/update/', ProfileUpdateView.as_view(), name='profile_update'),
  path('accounts/store/signup', StoreSignupView.as_view(), name='store_signup'),
  path('store/dashboard', StoreDashboard.as_view(), name='store_dashboard'),
  # overriding default allauth urls
  path('accounts/signup/', CustomSignupView.as_view(), name='account_signup'),
  path('accounts/login/', CustomLoginView.as_view(), name='account_login'),

  path('accounts/register/', RegisterPage.as_view(), name='register'),
  path('accounts/', include("allauth.urls")),
  path('', HomePageView.as_view(), name='home'),
]