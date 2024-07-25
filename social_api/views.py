from datetime import timedelta

from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Post, Like, Comment
from .serializers import (
    PostSerializer,
    LikeSerializer,
    CommentSerializer,
    SchedulePostSerializer,
    PostListSerializer,
    PostDetailSerializer,
    PostImageSerializer,
)
from .tasks import create_scheduled_post


class PostViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        if self.action == "upload_image":
            return PostImageSerializer
        return PostSerializer

    @action(detail=False, methods=["post"])
    def schedule_post_creation(self, request):
        """
        Schedule a post creation.
        """
        serializer = SchedulePostSerializer(data=request.data)
        if serializer.is_valid():
            content = serializer.validated_data.get("content")
            hashtags = serializer.validated_data.get("hashtags", "")
            delay_minutes = serializer.validated_data.get("delay_minutes", 1)

            eta = timezone.now() + timedelta(minutes=delay_minutes)
            create_scheduled_post.apply_async(
                (request.user.id, content, None, hashtags), eta=eta
            )

            return Response({"status": "Post creation scheduled"}, status=200)
        return Response(serializer.errors, status=400)

    def get_queryset(self):
        user = self.request.user
        queryset = Post.objects.all()

        if self.action == "list" and "liked" in self.request.query_params:
            return queryset.filter(likes__user=user)

        hashtags = self.request.query_params.get("hashtags")
        if hashtags:
            queryset = queryset.filter(content__icontains=hashtags)

        filter_by = self.request.query_params.get("filter_by")
        if filter_by == "own":
            queryset = queryset.filter(author=user)
        elif filter_by == "following":
            following_users = user.following.all()
            queryset = queryset.filter(author__in=following_users)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="post",
                type=OpenApiTypes.INT,
                description="Filter by post id (ex. ?post=2)",
            ),
            OpenApiParameter(
                name="date",
                type=OpenApiTypes.DATE,
                description="Filter by datetime of Post (ex. ?date=2022-10-23)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.queryset

        post_id = request.query_params.get("post")
        date = request.query_params.get("date")

        if post_id:
            queryset = queryset.filter(id=post_id)
        if date:
            queryset = queryset.filter(created_at__date=date)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class LikeViewSet(
    viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.DestroyModelMixin
):
    queryset = Like.objects.all().select_related("user", "post")
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        post = serializer.validated_data["post"]
        if post.author == self.request.user:
            raise PermissionDenied("You cannot like your own post.")
        if Like.objects.filter(user=self.request.user, post=post).exists():
            raise PermissionDenied("You have already liked this post.")
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        post = self.kwargs.get("pk")
        like = Like.objects.filter(user=request.user, post_id=post).first()
        if like:
            like.delete()
            return Response(
                {"detail": "Post unliked"}, status=status.HTTP_204_NO_CONTENT
            )
        return Response({"detail": "Not liked yet"}, status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        post = serializer.validated_data["post"]
        if post.author == self.request.user:
            raise PermissionDenied("You cannot comment on your own post.")
        serializer.save(user=self.request.user)

    def get_queryset(self):
        post_id = self.kwargs.get("post_pk")
        if post_id:
            return Comment.objects.filter(post_id=post_id)
        return super().get_queryset()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="post",
                type=OpenApiTypes.INT,
                description="Filter by post id (ex. ?post=2)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        post_id = request.query_params.get("post")

        if post_id:
            queryset = queryset.filter(post_id=post_id)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
