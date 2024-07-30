from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from social_api.models import Post
from django.utils import timezone

User = get_user_model()
POST_URL = reverse("social_api:post-list")


class PostViewSetTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@gmail.com", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)

    def test_create_post(self):
        data = {
            "content": "Test post content",
            "hashtags": ["test"],
        }
        response = self.client.post(POST_URL, data)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.get().content, "Test post content")

    def test_create_post_unauthorized(self):
        self.client.force_authenticate(user=None)
        data = {
            "content": "Test post content",
            "hashtags": ["test"],
        }
        response = self.client.post(POST_URL, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_post_missing_field(self):
        data = {
            "content": "",
        }
        response = self.client.post(POST_URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_posts(self):
        Post.objects.create(author=self.user, content="Post 1")
        Post.objects.create(author=self.user, content="Post 2")
        response = self.client.get(POST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_posts_by_id(self):
        post = Post.objects.create(author=self.user, content="Post to be filtered")
        response = self.client.get(POST_URL, {"post": post.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_posts_by_date(self):
        post = Post.objects.create(
            author=self.user, content="Post with date", created_at=timezone.now()
        )
        response = self.client.get(POST_URL, {"date": post.created_at.date()})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
