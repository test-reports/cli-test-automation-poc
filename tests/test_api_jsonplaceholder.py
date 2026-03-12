"""Basic API tests for JSONPlaceholder (https://jsonplaceholder.typicode.com)."""

import pytest
import requests

BASE_URL = "https://jsonplaceholder.typicode.com"


def test_get_posts_returns_200():
    """GET /posts returns status 200."""
    r = requests.get(f"{BASE_URL}/posts")
    assert r.status_code == 200
#test changes

def test_get_posts_returns_list():
    """GET /posts returns a list of posts."""
    r = requests.get(f"{BASE_URL}/posts")
    data = r.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_single_post_has_expected_keys():
    """GET /posts/1 returns an object with id, title, body, userId."""
    r = requests.get(f"{BASE_URL}/posts/1")
    assert r.status_code == 200
    post = r.json()
    assert "id" in post
    assert "title" in post
    assert "body" in post
    assert "userId" in post


def test_get_users_returns_200():
    """GET /users returns status 200."""
    r = requests.get(f"{BASE_URL}/users")
    assert r.status_code == 200


def test_get_posts_returns_exactly_100_posts():
    """GET /posts returns exactly 100 posts. (Intentional failure: API returns 100, we assert 99.)"""
    r = requests.get(f"{BASE_URL}/posts")
    assert r.status_code == 200
    data = r.json()
    count = len(data)
    assert count == 99, f"Expected 99 posts, got {count}"  # Failing: API returns 100
