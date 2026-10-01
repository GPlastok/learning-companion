import pytest
from conftest import signup_data
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_ac10_signup_stores_names_and_email(client, django_user_model):
    response = client.get(reverse("signup"))

    assert response.status_code == 200
    assert "accounts/signup.html" in [t.name for t in response.templates]

    client.post(reverse("signup"), signup_data())

    user = django_user_model.objects.get(username="linus")
    assert user.email == "linus@example.com"
    assert user.first_name == "Linus"
    assert user.last_name == "Torvalds"


@pytest.mark.parametrize("field", ["first_name", "last_name", "email"])
def test_ac10_signup_requires_names_and_email(client, django_user_model, field):
    response = client.post(reverse("signup"), signup_data(**{field: ""}))

    assert response.status_code == 200
    assert field in response.context["form"].errors
    assert not django_user_model.objects.exists()


def test_ac11_signup_logs_in_and_redirects_home(client):
    response = client.post(reverse("signup"), signup_data(), follow=True)

    assert response.redirect_chain[-1][0] == reverse("home")
    assert response.wsgi_request.user.is_authenticated


@pytest.mark.parametrize(
    ("overrides", "field"),
    [
        pytest.param({"username": "ada"}, "username", id="taken_username"),
        pytest.param({"username": "ADA"}, "username", id="taken_username_other_case"),
        pytest.param(
            {"password2": "Different-pw-99"}, "password2", id="password_mismatch"
        ),
        pytest.param(
            {"password1": "12345678", "password2": "12345678"},
            "password2",
            id="weak_password",
        ),
    ],
)
def test_ac2_signup_rejects_invalid_data(
    client, user, django_user_model, overrides, field
):
    response = client.post(reverse("signup"), signup_data(**overrides))

    assert response.status_code == 200
    assert field in response.context["form"].errors
    assert django_user_model.objects.count() == 1


@pytest.mark.parametrize("email", ["ada@example.com", "ADA@Example.com"])
def test_ac9_signup_rejects_taken_email(client, user, django_user_model, email):
    response = client.post(reverse("signup"), signup_data(email=email))

    assert response.status_code == 200
    assert "email" in response.context["form"].errors
    assert django_user_model.objects.count() == 1


def test_ac23_signup_rejects_at_in_username(client, django_user_model):
    response = client.post(reverse("signup"), signup_data(username="ada@example.com"))

    assert response.status_code == 200
    assert "username" in response.context["form"].errors
    assert not django_user_model.objects.exists()
