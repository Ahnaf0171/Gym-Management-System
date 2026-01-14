from rest_framework import viewsets, mixins, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from .models import User
from .serializers import UserReadSerializer, UserCreateSerializer, LoginSerializer

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserReadSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )

class TokenRefreshView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh = RefreshToken(refresh_token)
            return Response(
                {"access": str(refresh.access_token)},
                status=status.HTTP_200_OK,
            )
        except (TokenError, InvalidToken):
            return Response(
                {"detail": "Invalid or expired refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

class UserViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = User.objects.select_related("gym_branch").filter(is_active=True)
        user = self.request.user

        if user.role == User.SUPER_ADMIN:
            return qs
        if user.role == User.MANAGER:
            return qs.filter(gym_branch_id=user.gym_branch_id)

        return User.objects.none()

    def get_serializer_class(self):
        return UserCreateSerializer if self.action == "create" else UserReadSerializer

    def create(self, request, *args, **kwargs):
        if request.user.role not in [User.SUPER_ADMIN, User.MANAGER]:
            return Response(
                {"detail": "You do not have permission to create users."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        return Response(UserReadSerializer(request.user).data, status=status.HTTP_200_OK)
