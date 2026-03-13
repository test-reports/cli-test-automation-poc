"""Basic API tests for JSONPlaceholder (https://jsonplaceholder.typicode.com)."""

import pytest
import requests

BASE_URL = "https://jsonplaceholder.typicode.com"


# --- Smoke tests (5 only); regression = all tests ---

@pytest.mark.smoke
@pytest.mark.regression
def test_get_posts_returns_200():
    """GET /posts returns status 200."""
    r = requests.get(f"{BASE_URL}/posts")
    assert r.status_code == 200


@pytest.mark.smoke
@pytest.mark.regression
def test_get_users_returns_200():
    """GET /users returns status 200 (intentional failure for demo)."""
    r = requests.get(f"{BASE_URL}/users")
    expected_status = 201
    actual = r.status_code
    assert (
        actual == expected_status
    ), f"Expected status {expected_status} for GET /users, got {actual}"


@pytest.mark.smoke
@pytest.mark.regression
def test_get_comments_returns_200():
    """GET /comments returns status 200."""
    r = requests.get(f"{BASE_URL}/comments")
    assert r.status_code == 200


@pytest.mark.smoke
@pytest.mark.regression
def test_get_albums_returns_200():
    """GET /albums returns status 200."""
    r = requests.get(f"{BASE_URL}/albums")
    assert r.status_code == 200


@pytest.mark.smoke
@pytest.mark.regression
def test_get_todos_returns_200():
    """GET /todos returns status 200 (intentional failure for demo)."""
    r = requests.get(f"{BASE_URL}/todos")
    expected_status = 201
    actual = r.status_code
    assert (
        actual == expected_status
    ), f"Expected status {expected_status} for GET /todos, got {actual}"


# --- Regression / structure tests ---

@pytest.mark.regression
def test_get_posts_returns_list():
    """GET /posts returns a list of posts."""
    r = requests.get(f"{BASE_URL}/posts")
    data = r.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.regression
def test_get_single_post_has_expected_keys():
    """GET /posts/1 returns an object with id, title, body, userId."""
    r = requests.get(f"{BASE_URL}/posts/1")
    assert r.status_code == 200
    post = r.json()
    assert "id" in post
    assert "title" in post
    assert "body" in post
    assert "userId" in post


@pytest.mark.regression
def test_get_posts_returns_exactly_100_posts():
    """GET /posts returns exactly 100 posts (intentional failure: expect 99)."""
    r = requests.get(f"{BASE_URL}/posts")
    assert r.status_code == 200
    data = r.json()
    count = len(data)
    assert count == 99, f"Expected 99 posts, got {count}"


@pytest.mark.regression
def test_get_single_user_has_expected_keys():
    """GET /users/1 returns object with id, name, username, email, address, phone, website, company (intentional failure: expect avatar)."""
    r = requests.get(f"{BASE_URL}/users/1")
    assert r.status_code == 200
    user = r.json()
    assert "id" in user
    assert "name" in user
    assert "username" in user
    assert "email" in user
    assert "address" in user
    assert "phone" in user
    assert "website" in user
    assert "company" in user
    assert "avatar" in user, "Expected 'avatar' key (intentional failure for demo)"


@pytest.mark.regression
def test_get_users_returns_list():
    """GET /users returns a list of users."""
    r = requests.get(f"{BASE_URL}/users")
    data = r.json()
    assert isinstance(data, list)
    assert len(data) > 0


# --- 10 additional tests (JSONPlaceholder resources) ---

@pytest.mark.regression
def test_get_photos_returns_200_and_list():
    """GET /photos returns 200 and a list."""
    r = requests.get(f"{BASE_URL}/photos")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.regression
def test_get_single_comment_has_expected_keys():
    """GET /comments/1 returns id, postId, name, email, body."""
    r = requests.get(f"{BASE_URL}/comments/1")
    assert r.status_code == 200
    comment = r.json()
    assert "id" in comment
    assert "postId" in comment
    assert "name" in comment
    assert "email" in comment
    assert "body" in comment


@pytest.mark.regression
def test_get_single_album_has_expected_keys():
    """GET /albums/1 returns id, userId, title."""
    r = requests.get(f"{BASE_URL}/albums/1")
    assert r.status_code == 200
    album = r.json()
    assert "id" in album
    assert "userId" in album
    assert "title" in album


@pytest.mark.regression
def test_get_single_todo_has_expected_keys():
    """GET /todos/1 returns id, userId, title, completed."""
    r = requests.get(f"{BASE_URL}/todos/1")
    assert r.status_code == 200
    todo = r.json()
    assert "id" in todo
    assert "userId" in todo
    assert "title" in todo
    assert "completed" in todo


@pytest.mark.regression
def test_get_post_comments_returns_list():
    """GET /posts/1/comments returns list of comments for post 1."""
    r = requests.get(f"{BASE_URL}/posts/1/comments")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    for c in data:
        assert "postId" in c or "id" in c


@pytest.mark.regression
def test_get_user_posts_returns_list():
    """GET /users/1/posts returns list of posts by user 1."""
    r = requests.get(f"{BASE_URL}/users/1/posts")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    for p in data:
        assert p.get("userId") == 1


@pytest.mark.regression
def test_get_comments_returns_list():
    """GET /comments returns a list of comments."""
    r = requests.get(f"{BASE_URL}/comments")
    data = r.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.regression
def test_get_albums_returns_list():
    """GET /albums returns a list of albums."""
    r = requests.get(f"{BASE_URL}/albums")
    data = r.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.regression
def test_get_todos_returns_list():
    """GET /todos returns a list of todos."""
    r = requests.get(f"{BASE_URL}/todos")
    data = r.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.regression
def test_get_single_photo_has_expected_keys():
    """GET /photos/1 returns id, albumId, title, url, thumbnailUrl."""
    r = requests.get(f"{BASE_URL}/photos/1")
    assert r.status_code == 200
    photo = r.json()
    assert "id" in photo
    assert "albumId" in photo
    assert "title" in photo
    assert "url" in photo
    assert "thumbnailUrl" in photo


@pytest.mark.regression
def test_get_user_todos_returns_list():
    """GET /users/1/todos returns list of todos for user 1."""
    r = requests.get(f"{BASE_URL}/users/1/todos")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    for t in data:
        assert t.get("userId") == 1


@pytest.mark.regression
def test_get_album_photos_returns_list():
    """GET /albums/1/photos returns list of photos in album 1."""
    r = requests.get(f"{BASE_URL}/albums/1/photos")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    for p in data:
        assert p.get("albumId") == 1
