from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from social_api.models import Post, Like

User = get_user_model()

LIKE_URL = reverse("social_api:like-list")


class LikeViewSetTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@gmail.com", password="testpassword"
        )
        self.other_user = User.objects.create_user(
            email="other@gmail.com", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)

        self.post = Post.objects.create(author=self.other_user, content="Post to like")

    def test_like_post(self):
        data = {"post": self.post.id}
        response = self.client.post(LIKE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 1)
        self.assertEqual(Like.objects.get().user, self.user)
        self.assertEqual(Like.objects.get().post, self.post)

    def test_like_own_post(self):
        own_post = Post.objects.create(author=self.user, content="My own post")
        data = {"post": own_post.id}
        response = self.client.post(LIKE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_like_post_twice(self):
        data = {"post": self.post.id}
        self.client.post(LIKE_URL, data)
        response = self.client.post(LIKE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unlike_post(self):
        like = Like.objects.create(user=self.user, post=self.post)
        url = reverse("social_api:like-detail", args=[self.post.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Like.objects.count(), 0)

    def test_unlike_not_liked_post(self):
        url = reverse("social_api:like-detail", args=[self.post.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
