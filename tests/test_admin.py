import pytest
from django.contrib import admin
from django.urls import reverse

from accounts.models import Cohort, Profile, User
from core.models import Tag
from learning.models import Goal, LearningSession


@pytest.mark.parametrize("model", [User, Profile, Cohort, Tag])
def test_ac22_models_registered_in_admin(model):
    assert admin.site.is_registered(model)


@pytest.mark.parametrize("model", [Goal, LearningSession])
def test_ac41_learning_models_registered_in_admin(model):
    assert admin.site.is_registered(model)


def test_ac22_staff_lists_profiles(admin_client, user, other_user):
    response = admin_client.get(reverse("admin:accounts_profile_changelist"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "ada" in content
    assert "grace" in content
