from django.contrib.auth import get_user_model
from rest_framework import status, generics, permissions
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from .serializers import UserSerializer, LogoutSerializer, FollowUnfollowSerializer
from social_api.permissions import IsOwnerReadOnly

CustomerUser = get_user_model()


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    serializer_class = AuthTokenSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class UsersList(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = CustomerUser.objects.all()
        username = self.request.query_params.get("username")
        email = self.request.query_params.get("email")
        bio = self.request.query_params.get("bio")

        if username:
            queryset = queryset.filter(username__icontains=username)
        if email:
            queryset = queryset.filter(email__icontains=email)
        if bio:
            queryset = queryset.filter(bio__icontains=bio)

        return queryset


class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomerUser.objects.all()
    serializer_class = UserSerializer
    lookup_field = "email"


class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsOwnerReadOnly)

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowUnfollowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = FollowUnfollowSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user_to_follow = get_object_or_404(CustomerUser, email=email)
        request.user.follow(user_to_follow)
        return Response(
            {"detail": f"You are now following {email}"}, status=status.HTTP_200_OK
        )

    def delete(self, request, *args, **kwargs):
        serializer = FollowUnfollowSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user_to_unfollow = get_object_or_404(CustomerUser, email=email)
        request.user.unfollow(user_to_unfollow)
        return Response(
            {"detail": f"You have unfollowed {email}"}, status=status.HTTP_200_OK
        )

    def get(self, request, *args, **kwargs):
        view_type = request.query_params.get("view_type")
        if view_type == "following":
            following_users = request.user.following.all()
            serializer = UserSerializer(following_users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif view_type == "followers":
            followers = request.user.followers.all()
            serializer = UserSerializer(followers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": "Invalid view_type parameter"},
                status=status.HTTP_400_BAD_REQUEST,
            )
