from .views import (
    RegisterAPIView,
    LoginAPIView,
    LogoutAPIView,
    UserProfileAPIView,
    TokenRefreshAPIView,
)
from django.urls import path

app_name = "authentication"

urlpatterns = [
    # API views
    path("register/", RegisterAPIView.as_view(), name="api-register"),
    path("login/", LoginAPIView.as_view(), name="api-login"),
    path("logout/", LogoutAPIView.as_view(), name="api-logout"),
    path("refresh/", TokenRefreshAPIView.as_view(), name="api-token-refresh"),
    path("profile/", UserProfileAPIView.as_view(), name="api-profile"),
]
