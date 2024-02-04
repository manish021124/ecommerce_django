from django.urls import include, path
from . import views
from .views import HomePageView, RegisterPage, CustomSignupView, CustomLoginView

urlpatterns = [
  # overriding default allauth urls
  path('accounts/signup/', CustomSignupView.as_view(), name='account_signup'),
  path('accounts/login/', CustomLoginView.as_view(), name='account_login'),

  path('accounts/register/', RegisterPage.as_view(), name='register'),
  path('accounts/', include("allauth.urls")),
  path('', HomePageView.as_view(), name='home'),
]