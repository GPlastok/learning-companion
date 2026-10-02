import re
from datetime import date, timedelta

import pytest
from conftest import session_data
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from core.models import Tag
from learning.models import Goal, LearningSession

pytestmark = pytest.mark.django_db


def test_ac12_create_session_appears_in_list(logged_in_client, goal):
    response = logged_in_client.post(
        reverse("session_create"), session_data(goal, notes="Wrote model tests")
    )

    assert response.status_code == 302
    assert response.url == reverse("session_list")
    session = LearningSession.objects.get(goal=goal)
    assert session.date == date(2026, 9, 30)
    assert session.duration_minutes == 90
    assert session.notes == "Wrote model tests"
    content = logged_in_client.get(reverse("session_list")).content.decode()
    assert "Wrote model tests" in content
    assert "Learn Django" in content
    assert f'href="{reverse("session_create")}"' in content


def test_ac13_form_offers_only_own_goals(logged_in_client, goal, other_goal):
    response = logged_in_client.get(reverse("session_create"))

    assert list(response.context["form"].fields["goal"].queryset) == [goal]

    response = logged_in_client.post(
        reverse("session_create"), session_data(other_goal)
    )

    assert response.status_code == 200
    assert "goal" in response.context["form"].errors
    assert LearningSession.objects.count() == 0


def test_ac14_tags_are_saved_and_shown(logged_in_client, goal):
    tags = Tag.objects.filter(name__in=["Python", "Testing"])

    logged_in_client.post(
        reverse("session_create"), session_data(goal, tags=[t.pk for t in tags])
    )

    session = LearningSession.objects.get(goal=goal)
    assert set(session.tags.values_list("name", flat=True)) == {"Python", "Testing"}
    content = logged_in_client.get(reverse("session_list")).content.decode()
    assert "Python" in content
    assert "Testing" in content
    form = logged_in_client.get(reverse("session_create")).context["form"]
    assert form.fields["tags"].queryset.count() == Tag.objects.count()


def test_ac15_session_without_tags_saves(logged_in_client, goal):
    response = logged_in_client.post(reverse("session_create"), session_data(goal))

    assert response.status_code == 302
    assert LearningSession.objects.get(goal=goal).tags.count() == 0


def test_ac19_list_shows_only_own_sessions(logged_in_client, session, other_session):
    content = logged_in_client.get(reverse("session_list")).content.decode()

    assert "Read the ORM docs" in content
    assert "Borrow checker" not in content


def test_ac34_no_goals_shows_create_a_goal_first(logged_in_client):
    content = logged_in_client.get(reverse("session_create")).content.decode()

    assert "Create a goal first" in content
    assert f'href="{reverse("goal_create")}"' in content
    assert 'name="date"' not in content


@pytest.mark.parametrize(
    ("overrides", "field"),
    [
        pytest.param({"date": ""}, "date", id="no_date"),
        pytest.param({"hours": "", "minutes": ""}, "hours", id="no_duration"),
        pytest.param({"hours": 0, "minutes": 0}, "__all__", id="zero"),
        pytest.param({"hours": -1, "minutes": 0}, "hours", id="negative"),
    ],
)
def test_ac16_invalid_session_is_rejected(logged_in_client, goal, overrides, field):
    response = logged_in_client.post(
        reverse("session_create"), session_data(goal, **overrides)
    )

    assert response.status_code == 200
    assert field in response.context["form"].errors
    assert LearningSession.objects.count() == 0


def test_ac30_duration_hours_and_minutes(logged_in_client, goal):
    response = logged_in_client.post(
        reverse("session_create"), session_data(goal, minutes=60)
    )

    assert "minutes" in response.context["form"].errors
    assert LearningSession.objects.count() == 0

    logged_in_client.post(
        reverse("session_create"), session_data(goal, hours=2, minutes=5)
    )

    assert LearningSession.objects.get(goal=goal).duration_minutes == 125


def test_ac31_date_today_or_earlier(logged_in_client, goal):
    assert settings.TIME_ZONE == "Europe/Berlin"

    response = logged_in_client.get(reverse("session_create"))

    assert response.context["form"]["date"].value() == timezone.localdate()

    tomorrow = timezone.localdate() + timedelta(days=1)
    response = logged_in_client.post(
        reverse("session_create"), session_data(goal, date=tomorrow.isoformat())
    )

    assert "date" in response.context["form"].errors
    assert LearningSession.objects.count() == 0

    response = logged_in_client.post(
        reverse("session_create"),
        session_data(goal, date=timezone.localdate().isoformat()),
    )

    assert response.status_code == 302


def test_ac17_edit_session_shows_new_values(logged_in_client, goal, session):
    url = reverse("session_edit", args=[session.pk])
    form = logged_in_client.get(url).context["form"]

    assert form["hours"].value() == 1
    assert form["minutes"].value() == 30

    response = logged_in_client.post(
        url, session_data(goal, hours=0, minutes=45, notes="Read about querysets")
    )

    assert response.status_code == 302
    assert response.url == reverse("session_list")
    session.refresh_from_db()
    assert session.duration_minutes == 45
    content = logged_in_client.get(reverse("session_list")).content.decode()
    assert "Read about querysets" in content
    assert "Read the ORM docs" not in content


def test_ac32_edit_moves_session_to_another_goal(logged_in_client, user, session):
    docker = Goal.objects.create(user=user, title="Learn Docker")

    logged_in_client.post(
        reverse("session_edit", args=[session.pk]), session_data(docker)
    )

    session.refresh_from_db()
    assert session.goal == docker


def test_ac18_delete_session_after_confirmation(logged_in_client, session):
    url = reverse("session_delete", args=[session.pk])
    content = logged_in_client.get(reverse("session_list")).content.decode()

    assert f'hx-post="{url}"' in content
    assert 'hx-confirm="Delete this session?"' in content

    response = logged_in_client.get(url)

    assert response.status_code == 405
    assert LearningSession.objects.filter(pk=session.pk).exists()

    response = logged_in_client.post(url)

    assert response.status_code == 302
    assert response.url == reverse("session_list")
    assert not LearningSession.objects.filter(pk=session.pk).exists()
    content = logged_in_client.get(reverse("session_list")).content.decode()
    assert "Read the ORM docs" not in content


@pytest.mark.parametrize("target", ["other", "missing"])
@pytest.mark.parametrize(
    ("method", "name"),
    [
        pytest.param("get", "session_edit", id="edit_get"),
        pytest.param("post", "session_edit", id="edit_post"),
        pytest.param("post", "session_delete", id="delete_post"),
    ],
)
def test_ac20_other_users_session_is_404(
    logged_in_client, other_session, method, name, target
):
    pk = other_session.pk if target == "other" else 999999
    url = reverse(name, args=[pk])

    if method == "get":
        response = logged_in_client.get(url)
    else:
        response = logged_in_client.post(
            url, session_data(other_session.goal, minutes=1)
        )

    assert response.status_code == 404
    other_session.refresh_from_db()
    assert other_session.duration_minutes == 45


def test_ac29_htmx_delete_removes_row(logged_in_client, session):
    url = reverse("session_delete", args=[session.pk])
    content = logged_in_client.get(reverse("session_list")).content.decode()
    form = re.search(rf'<form[^>]+hx-post="{url}"[^>]*>', content)

    assert form
    assert 'hx-target="closest li"' in form.group(0)
    assert 'hx-swap="outerHTML"' in form.group(0)

    response = logged_in_client.post(url, headers={"HX-Request": "true"})

    assert response.status_code == 200
    assert f'id="session-{session.pk}"' not in response.content.decode()
    assert not LearningSession.objects.filter(pk=session.pk).exists()


def row(content, element_id):
    start = content.index(f'id="{element_id}"')
    return content[start : content.index("</li>", start)]


def test_ac36_session_rows(logged_in_client, goal, session):
    session.tags.add(Tag.objects.get(name="Python"))
    LearningSession.objects.create(
        goal=goal, date=date(2026, 10, 1), duration_minutes=30, notes="Later one"
    )

    content = logged_in_client.get(reverse("session_list")).content.decode()

    assert content.index("Later one") < content.index("Read the ORM docs")
    session_row = row(content, f"session-{session.pk}")
    for text in [
        "30 Sep 2026",
        "Learn Django",
        "1 h 30 min",
        "Python",
        "Read the ORM docs",
    ]:
        assert text in session_row
    assert "Then tried annotate" not in session_row


def test_ac21_no_sessions_empty_state(logged_in_client, goal):
    content = logged_in_client.get(reverse("session_list")).content.decode()

    assert "No sessions yet." in content


def test_ac33_filter_by_goal(logged_in_client, user, goal, session, other_session):
    docker = Goal.objects.create(user=user, title="Learn Docker")
    LearningSession.objects.create(
        goal=docker, date=date(2026, 9, 29), duration_minutes=20, notes="Docker notes"
    )
    url = reverse("session_list")

    content = logged_in_client.get(url + f"?goal={goal.pk}").content.decode()

    assert "Read the ORM docs" in content
    assert "Docker notes" not in content

    for value in [other_session.goal.pk, "abc", "²"]:
        content = logged_in_client.get(url + f"?goal={value}").content.decode()

        assert "Read the ORM docs" in content
        assert "Docker notes" in content
        assert "Borrow checker" not in content

    content = logged_in_client.get(url).content.decode()
    form = re.search(r"<form[^>]+hx-get[^>]*>(?:(?!</form>)[\s\S])*</form>", content)
    assert form
    assert 'hx-target="#session-list"' in form.group(0)
    assert 'hx-trigger="change, submit"' in form.group(0)
    assert 'hx-push-url="true"' in form.group(0)
    select = re.search(r'<select name="goal"[^>]*>([\s\S]*?)</select>', form.group(0))
    assert select
    options = re.findall(r"<option[^>]*>\s*([^<]*?)\s*</option>", select.group(1))
    assert options == ["All goals", "Learn Docker", "Learn Django"]

    response = logged_in_client.get(
        url + f"?goal={goal.pk}", headers={"HX-Request": "true"}
    )

    names = [t.name for t in response.templates]
    assert "learning/_session_list.html" in names
    assert "base.html" not in names


def test_ac43_history_restore_gets_full_page(logged_in_client, goal):
    url = reverse("session_list") + f"?goal={goal.pk}"

    response = logged_in_client.get(
        url, headers={"HX-Request": "true", "HX-History-Restore-Request": "true"}
    )

    names = [t.name for t in response.templates]
    assert "base.html" in names
    assert "learning/session_list.html" in names

    response = logged_in_client.get(url, headers={"HX-Request": "true"})

    assert "HX-Request" in response["Vary"]


@pytest.mark.parametrize(
    ("overrides", "field"),
    [
        pytest.param({"hours": 25, "minutes": 0}, "hours", id="25_hours"),
        pytest.param({"hours": 24, "minutes": 1}, "__all__", id="24_hours_1_min"),
        pytest.param({"hours": 10**18, "minutes": 0}, "hours", id="huge"),
    ],
)
def test_ac42_session_longer_than_24_hours_is_rejected(
    logged_in_client, goal, overrides, field
):
    response = logged_in_client.post(
        reverse("session_create"), session_data(goal, **overrides)
    )

    assert response.status_code == 200
    assert field in response.context["form"].errors
    assert LearningSession.objects.count() == 0


def test_ac42_exactly_24_hours_saves(logged_in_client, goal):
    response = logged_in_client.post(
        reverse("session_create"), session_data(goal, hours=24, minutes=0)
    )

    assert response.status_code == 302
    assert LearningSession.objects.get(goal=goal).duration_minutes == 1440
