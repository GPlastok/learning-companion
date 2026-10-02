import pytest
from django.core.management import call_command
from django.urls import reverse

from learning.models import Goal, LearningSession, Resource

pytestmark = pytest.mark.django_db


def test_ac23_account_delete_removes_goals_and_sessions(
    logged_in_client, user, goal, session, other_session
):
    logged_in_client.post(reverse("account_delete"))

    assert not Goal.objects.filter(user__pk=user.pk).exists()
    assert not LearningSession.objects.filter(goal__user__pk=user.pk).exists()
    assert LearningSession.objects.filter(pk=other_session.pk).exists()


def test_ac18_goal_delete_removes_resources(
    logged_in_client, goal, resource, other_resource
):
    logged_in_client.post(reverse("goal_delete", args=[goal.pk]))

    assert not Resource.objects.filter(goal__pk=goal.pk).exists()
    assert Resource.objects.filter(pk=other_resource.pk).exists()


def test_ac18_account_delete_removes_resources(
    logged_in_client, user, resource, other_resource
):
    logged_in_client.post(reverse("account_delete"))

    assert not Resource.objects.filter(goal__user__pk=user.pk).exists()
    assert Resource.objects.filter(pk=other_resource.pk).exists()


def test_ac24_migrations_are_committed():
    call_command("makemigrations", "--check", "--dry-run")
