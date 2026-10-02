from datetime import date

import pytest

from learning.models import Goal, LearningSession

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


def goal_data(**overrides):
    data = {"title": "Learn Docker", "description": "", "status": "planned"}
    data.update(overrides)
    return data


def session_data(goal, **overrides):
    data = {
        "goal": goal.pk,
        "date": "2026-09-30",
        "hours": 1,
        "minutes": 30,
        "notes": "Wrote tests",
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
def goal(user):
    return Goal.objects.create(
        user=user, title="Learn Django", description="Models and views"
    )


@pytest.fixture
def other_goal(other_user):
    return Goal.objects.create(user=other_user, title="Learn Rust")


@pytest.fixture
def session(goal):
    return LearningSession.objects.create(
        goal=goal,
        date=date(2026, 9, 30),
        duration_minutes=90,
        notes="Read the ORM docs\nThen tried annotate",
    )


@pytest.fixture
def other_session(other_goal):
    return LearningSession.objects.create(
        goal=other_goal,
        date=date(2026, 9, 29),
        duration_minutes=45,
        notes="Borrow checker",
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
