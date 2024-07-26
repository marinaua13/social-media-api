from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()
CREATE_USER_URL = reverse("user:create")
MANAGE_USER_URL = reverse("user:manage")


class UserTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)

    def test_create_user_success(self):
        data = {
            "email": "newuser@example.com",
            "password": "newpassword",
        }
        response = self.client.post(CREATE_USER_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=data["email"])
        self.assertTrue(user.check_password(data["password"]))

    def test_create_user_with_existing_email(self):
        data = {
            "email": "testuser@example.com",
            "password": "testpassword",
        }
        response = self.client.post(CREATE_USER_URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_manage_user(self):
        response = self.client.get(MANAGE_USER_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_list_users(self):
        url = reverse("user:profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_user_profile(self):
        url = reverse("user:user-profile", args=[self.user.email])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_follow_user(self):
        url = reverse("user:follow-unfollow")
        follow_user = User.objects.create_user(
            email="followuser@example.com", password="followpassword"
        )
        data = {"email": follow_user.email}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.following.filter(email=follow_user.email).exists())

    def test_unfollow_user(self):
        url = reverse("user:follow-unfollow")
        follow_user = User.objects.create_user(
            email="followuser@example.com", password="followpassword"
        )
        self.user.follow(follow_user)
        data = {"email": follow_user.email}
        response = self.client.delete(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.user.following.filter(email=follow_user.email).exists())
