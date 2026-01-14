from rest_framework.routers import DefaultRouter
from .views import GymBranchViewSet

router = DefaultRouter()
router.register(r"branches", GymBranchViewSet, basename="branches")
urlpatterns = router.urls
