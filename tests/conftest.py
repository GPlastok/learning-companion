import pytest

PASSWORD = "Sup3r-secret-pw"


def signup_data(**overrides):
    data = {
        "username": "linus",
        "email": "linus@example.com",
        "first_name": "Linus",
        "last_name": "Torvalds",
        "password1": PASSWORD,
        "password2": PASSWORD,
    }
    data.update(overrides)
    return data


@pytest.fixture
def password():
    return PASSWORD


@pytest.fixture
def user(db, django_user_model, password):
    return django_user_model.objects.create_user(
        username="ada",
        email="ada@example.com",
        password=password,
        first_name="Ada",
        last_name="Lovelace",
    )


@pytest.fixture
def other_user(db, django_user_model, password):
    return django_user_model.objects.create_user(
        username="grace",
        email="grace@example.com",
        password=password,
        first_name="Grace",
        last_name="Hopper",
    )


@pytest.fixture
def staff_user(db, django_user_model, password):
    return django_user_model.objects.create_user(
        username="staff",
        email="staff@example.com",
        password=password,
        is_staff=True,
    )


@pytest.fixture
def logged_in_client(client, user):
    client.force_login(user)
    return client
