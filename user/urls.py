from django.urls import include, path
from . import views
from .views import HomePageView, CustomRegisterPage

urlpatterns = [
  path('accounts/', include("allauth.urls")),
  path('accounts/register/', CustomRegisterPage.as_view(), name='register'),
  # path('signup/', CustomUserCreationView.as_view(), name='signup'),
  path('', HomePageView.as_view(), name='home'),
]