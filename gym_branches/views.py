from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import role_required
from .models import GymBranch
from .serializers import GymBranchSerializer
from accounts.models import User  
from accounts.permissions import role_required  
from rest_framework.filters import SearchFilter   

class GymBranchViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,     
    mixins.DestroyModelMixin,     
    viewsets.GenericViewSet,
):
    serializer_class = GymBranchSerializer
    filter_backends = [SearchFilter]                  
    search_fields = ["name", "location"]              

    def get_queryset(self):
        return GymBranch.objects.all()

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), role_required(User.SUPER_ADMIN)()]
        return [IsAuthenticated(), role_required(User.SUPER_ADMIN, User.MANAGER)()]