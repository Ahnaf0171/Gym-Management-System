from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django.db.models import Prefetch
from accounts.permissions import role_required
from accounts.models import User
from .models import GymBranch
from .serializers import GymBranchSerializer, PublicGymBranchSerializer


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
        return GymBranch.objects.prefetch_related(
            Prefetch(
                'users',
                queryset=User.objects.filter(role=User.MANAGER),
                to_attr='managers'
            )
        ).all()

    def get_permissions(self):
        if self.action == "public_list":
            return [AllowAny()]
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), role_required(User.SUPER_ADMIN)()]
        return [IsAuthenticated(), role_required(User.SUPER_ADMIN, User.MANAGER)()]

    @action(detail=False, methods=['get'], permission_classes=[AllowAny], url_path='public')
    def public_list(self, request):
        queryset = GymBranch.objects.prefetch_related(
            Prefetch(
                'users',
                queryset=User.objects.filter(role=User.MANAGER),
                to_attr='managers'
            )
        )
        serializer = PublicGymBranchSerializer(queryset, many=True)
        return Response(serializer.data)