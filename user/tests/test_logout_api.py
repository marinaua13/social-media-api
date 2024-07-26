from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()
LOGOUT_URL = reverse("user:logout")


class LogoutTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)
        self.refresh_token = str(RefreshToken.for_user(self.user))

    def test_logout_with_invalid_token(self):
        response = self.client.post(LOGOUT_URL, {"refresh": "invalid_token"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_with_valid_token(self):
        response = self.client.post(LOGOUT_URL, {"refresh": self.refresh_token})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
