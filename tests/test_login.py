import re

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_ac12_login_redirects_home(client, user, password):
    response = client.post(
        reverse("login"), {"username": "ada", "password": password}, follow=True
    )

    assert response.redirect_chain[-1][0] == reverse("home")
    assert response.wsgi_request.user.is_authenticated


def test_ac12_logout_redirects_to_login(logged_in_client):
    response = logged_in_client.post(reverse("logout"), follow=True)

    assert response.redirect_chain[-1][0] == reverse("login")
    assert not response.wsgi_request.user.is_authenticated


def test_ac3_wrong_password_shows_error(client, user):
    response = client.post(
        reverse("login"), {"username": "ada", "password": "wrong-pw"}
    )

    assert response.status_code == 200
    assert response.context["form"].non_field_errors()
    assert "_auth_user_id" not in client.session


def test_ac6_session_survives_reload(client, user, password):
    client.post(reverse("login"), {"username": "ada", "password": password})

    client.get(reverse("home"))
    response = client.get(reverse("home"))

    assert response.wsgi_request.user == user


def test_ac20_login_page_shows_punchline(client):
    response = client.get(reverse("login"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "Set goals. Log sessions. See how far you've come." in content
    assert re.search(r'<form[\s\S]*name="username"', content)


def test_ac21_login_page_nav_has_logo_only(client):
    content = client.get(reverse("login")).content.decode()

    assert "<nav" in content
    assert re.search(
        rf'<a[^>]+href="{reverse("home")}"[^>]*>\s*Learning Companion\s*</a>', content
    )
    assert f'action="{reverse("logout")}"' not in content
    assert f'href="{reverse("profile")}"' not in content


@pytest.mark.parametrize("login", ["ada", "ada@example.com", "ADA@example.com"])
def test_ac8_login_accepts_username_or_email(client, user, password, login):
    response = client.post(
        reverse("login"), {"username": login, "password": password}, follow=True
    )

    assert response.redirect_chain[-1][0] == reverse("home")
    assert response.wsgi_request.user.is_authenticated


def test_ac24_logged_in_user_skips_login(logged_in_client):
    response = logged_in_client.get(reverse("login"))

    assert response.status_code == 302
    assert response.url == reverse("home")
