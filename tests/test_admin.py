import pytest
from django.contrib import admin
from django.urls import reverse

from accounts.models import Cohort, Profile, User
from core.models import Tag
from learning.models import Goal, LearningSession, Resource


@pytest.mark.parametrize("model", [User, Profile, Cohort, Tag])
def test_ac22_models_registered_in_admin(model):
    assert admin.site.is_registered(model)


@pytest.mark.parametrize("model", [Goal, LearningSession])
def test_ac41_learning_models_registered_in_admin(model):
    assert admin.site.is_registered(model)


def test_ac19_resource_registered_in_admin():
    assert admin.site.is_registered(Resource)


@pytest.mark.django_db
def test_ac19_staff_lists_resources(admin_client, resource):
    response = admin_client.get(reverse("admin:learning_resource_changelist"))

    assert response.status_code == 200
    assert "Django models docs" in response.content.decode()


def test_ac22_staff_lists_profiles(admin_client, user, other_user):
    response = admin_client.get(reverse("admin:accounts_profile_changelist"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "ada" in content
    assert "grace" in content


@pytest.mark.django_db
def test_ac19_admin_url_without_scheme_gets_https(admin_client, goal):
    response = admin_client.post(
        reverse("admin:learning_resource_add"),
        {"goal": goal.pk, "url": "example.com/x", "title": "Admin link", "type": "doc"},
    )

    assert response.status_code == 302
    assert Resource.objects.get(title="Admin link").url == "https://example.com/x"
