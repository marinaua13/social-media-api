from rest_framework import serializers

from social_api.models import Post, Like, Comment


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.id")
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "content",
            "created_at",
            "updated_at",
            "post_picture",
            "hashtags",
            "likes_count",
            "comments_count",
        )

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()


class PostListSerializer(PostSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "content",
            "likes_count",
            "comments_count",
        )


class PostDetailSerializer(PostSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "content",
            "created_at",
            "updated_at",
            "post_picture",
            "hashtags",
            "likes_count",
            "comments_count",
        )


class PostImageSerializer(serializers.ModelSerializer):
    post_picture = serializers.ImageField()

    class Meta:
        model = Post
        fields = ("post_picture",)


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.id")

    class Meta:
        model = Like
        fields = ("id", "user", "post")


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.id")

    class Meta:
        model = Comment
        fields = ["id", "user", "post", "content", "created_at"]


class SchedulePostSerializer(serializers.Serializer):
    content = serializers.CharField()
    hashtags = serializers.CharField(required=False, allow_blank=True)
    delay_minutes = serializers.IntegerField(min_value=1)
