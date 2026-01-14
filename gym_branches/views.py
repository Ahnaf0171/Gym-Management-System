from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import role_required
from .models import GymBranch
from .serializers import GymBranchSerializer

class GymBranchViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = GymBranchSerializer
    permission_classes = [IsAuthenticated, role_required("super_admin")]

    def get_queryset(self):
        return GymBranch.objects.all()
