from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoginView, TokenRefreshView, UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("", include(router.urls)),
]