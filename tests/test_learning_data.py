import pytest
from django.core.management import call_command
from django.urls import reverse

from learning.models import Goal, LearningSession

pytestmark = pytest.mark.django_db


def test_ac23_account_delete_removes_goals_and_sessions(
    logged_in_client, user, goal, session, other_session
):
    logged_in_client.post(reverse("account_delete"))

    assert not Goal.objects.filter(user__pk=user.pk).exists()
    assert not LearningSession.objects.filter(goal__user__pk=user.pk).exists()
    assert LearningSession.objects.filter(pk=other_session.pk).exists()


def test_ac24_migrations_are_committed():
    call_command("makemigrations", "--check", "--dry-run")
