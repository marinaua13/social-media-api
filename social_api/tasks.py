from django.utils import timezone
from celery import shared_task
from .models import Post
from django.contrib.auth import get_user_model


@shared_task
def create_scheduled_post(author_id, content, post_picture=None, hashtags=None):
    User = get_user_model()
    author = User.objects.get(id=author_id)
    Post.objects.create(
        author=author,
        content=content,
        post_picture=post_picture,
        hashtags=hashtags,
        created_at=timezone.now(),
    )
