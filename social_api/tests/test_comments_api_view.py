from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from social_api.models import Post, Comment

User = get_user_model()

COMMENT_URL = reverse("social_api:comment-list")


class CommentViewSetTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@gmail.com", password="testpassword"
        )
        self.other_user = User.objects.create_user(
            email="other@gmail.com", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)

        self.post = Post.objects.create(
            author=self.other_user, content="Post to comment"
        )

    def test_create_comment(self):
        data = {"post": self.post.id, "content": "Test comment"}
        response = self.client.post(COMMENT_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.get().content, "Test comment")
        self.assertEqual(Comment.objects.get().user, self.user)
        self.assertEqual(Comment.objects.get().post, self.post)

    def test_create_comment_on_own_post(self):
        own_post = Post.objects.create(author=self.user, content="My own post")
        data = {"post": own_post.id, "content": "Test comment"}
        response = self.client.post(COMMENT_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_comments(self):
        Comment.objects.create(user=self.user, post=self.post, content="Comment 1")
        Comment.objects.create(user=self.user, post=self.post, content="Comment 2")
        response = self.client.get(COMMENT_URL, {"post": self.post.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_comments_no_post(self):
        Comment.objects.create(user=self.user, post=self.post, content="Comment 1")
        response = self.client.get(COMMENT_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_comment(self):
        comment = Comment.objects.create(
            user=self.user, post=self.post, content="Comment to retrieve"
        )
        url = reverse("social_api:comment-detail", args=[comment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["content"], "Comment to retrieve")

    def test_update_comment(self):
        comment = Comment.objects.create(
            user=self.user, post=self.post, content="Comment to update"
        )
        url = reverse("social_api:comment-detail", args=[comment.id])
        data = {"content": "Updated comment"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertEqual(comment.content, "Updated comment")

    def test_delete_comment(self):
        comment = Comment.objects.create(
            user=self.user, post=self.post, content="Comment to delete"
        )
        url = reverse("social_api:comment-detail", args=[comment.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)
