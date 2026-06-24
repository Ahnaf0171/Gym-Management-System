from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginView, UserViewSet, DashboardStatsView, PublicTrainersByBranchView  

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("dashboard/stats/", DashboardStatsView.as_view(), name="dashboard-stats"),
    path("public/trainers/", PublicTrainersByBranchView.as_view(), name="public-trainers"),    
    path("", include(router.urls)),
]