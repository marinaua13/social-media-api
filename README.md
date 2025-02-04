# Social Media API :relaxed:

## Description
This project is a RESTful API for a social media platform. The API allows users to create profiles, follow other users, create and retrieve posts, manage likes and comments, and perform basic social media actions.

## Features

### User Registration and Authentication
- Users can register with their email and password to create an account.
- Users can log in with their credentials and receive a token for authentication.
- Users can log out and invalidate their token.

### User Profile
- Users can create and update their profile, including profile picture, bio, and other details.
- Users can retrieve their own profile and view profiles of other users.
- Users can search for users by username or other criteria.

### Follow/Unfollow
- Users can follow and unfollow other users.
- Users can view the list of users they are following and the list of users following them.

### Post Creation and Retrieval
- Users can create new posts with text content and optional media attachments (e.g., images).
- Users can retrieve their own posts and posts of users they are following.
- Users can retrieve posts by hashtags or other criteria.

### Likes and Comments (Optional)
- Users can like and unlike posts.
- Users can view the list of posts they have liked.
- Users can add comments to posts and view comments on posts.

### Schedule Post Creation using Celery (Optional)
- Users can schedule post creation by selecting the time to create the post before creating it.

### API Permissions
- Only authenticated users can perform actions such as creating posts, liking posts, and following/unfollowing users.
- Users can only update and delete their own posts and comments.
- Users can only update and delete their own profile.

## Technical Requirements
- Use Django and Django REST Framework to build the API.
- Use token-based authentication for user authentication.
- Use appropriate serializers for data validation and representation.
- Use appropriate views and viewsets for handling CRUD operations on models.
- Use appropriate URL routing for different API endpoints.
- Use appropriate permissions and authentication classes to implement API permissions.

## Installation

1. **Clone the repository**
    ```sh
    git clone https://github.com/marinaua13/social-media-api/
    cd social-media-api
    ```

2. **Create a virtual environment and activate it**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies**
    ```sh
    pip install -r requirements.txt
    ```

4. **Apply migrations**
    ```sh
    python manage.py migrate
    ```

5. **Create a superuser**
    ```sh
    python manage.py createsuperuser
    ```

6. **Run the development server**
    ```sh
    python manage.py runserver
    ```

### Additional data:
You can use the following data to get token:
    email: admin2@gmail.com
    password: admin12345

Or you can make new registration 
- `POST /api/user/register/` - Register a new user
:relaxed:

### Documentation
The API documentation is available at `api/doc/swagger/`. It includes sample API requests and responses for different endpoints.
