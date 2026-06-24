from rest_framework.routers import DefaultRouter
from .views import GymBranchViewSet

router = DefaultRouter()
router.register(r"", GymBranchViewSet, basename="branches")

app_name = "gym_branches"
urlpatterns = router.urls
