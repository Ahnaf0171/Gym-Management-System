from rest_framework.routers import DefaultRouter
from .views import WorkoutPlanViewSet, WorkoutTaskViewSet

router = DefaultRouter()
router.register(r"workout-plans", WorkoutPlanViewSet, basename="workout-plans")
router.register(r"workout-tasks", WorkoutTaskViewSet, basename="workout-tasks")

urlpatterns = router.urls
