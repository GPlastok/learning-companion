import re
from datetime import UTC, date, datetime, timedelta

import pytest
from conftest import goal_data
from django.urls import reverse
from django.utils import timezone

from learning.models import Goal, LearningSession

pytestmark = pytest.mark.django_db


def test_ac1_create_goal_appears_in_list(logged_in_client, user):
    response = logged_in_client.post(
        reverse("goal_create"),
        goal_data(
            title="Learn Docker",
            description="Images and volumes",
            status="in-progress",
        ),
    )

    assert response.status_code == 302
    assert response.url == reverse("goal_list")
    goal = Goal.objects.get(user=user)
    assert (goal.title, goal.description, goal.status) == (
        "Learn Docker",
        "Images and volumes",
        "in-progress",
    )
    content = logged_in_client.get(reverse("goal_list")).content.decode()
    assert "Learn Docker" in content
    assert f'href="{reverse("goal_create")}"' in content


def test_ac2_invalid_status_is_rejected(logged_in_client):
    response = logged_in_client.post(
        reverse("goal_create"), goal_data(status="archived")
    )

    assert response.status_code == 200
    assert "status" in response.context["form"].errors
    assert Goal.objects.count() == 0


def test_ac3_title_is_required(logged_in_client):
    response = logged_in_client.post(reverse("goal_create"), goal_data(title=""))

    assert response.status_code == 200
    assert "title" in response.context["form"].errors
    assert Goal.objects.count() == 0


def test_ac26_title_longer_than_200_is_rejected(logged_in_client):
    response = logged_in_client.post(reverse("goal_create"), goal_data(title="x" * 201))

    assert response.status_code == 200
    assert "title" in response.context["form"].errors
    assert Goal.objects.count() == 0


def test_ac7_list_shows_only_own_goals(logged_in_client, goal, other_goal):
    content = logged_in_client.get(reverse("goal_list")).content.decode()

    assert "Learn Django" in content
    assert "Learn Rust" not in content


def test_ac25_new_goal_starts_planned_without_description(logged_in_client, user):
    response = logged_in_client.get(reverse("goal_create"))

    assert response.context["form"]["status"].value() == "planned"

    logged_in_client.post(reverse("goal_create"), goal_data())

    assert Goal.objects.filter(user=user, description="").exists()


def test_ac4_edit_changes_updated_but_not_created(logged_in_client, goal):
    past = timezone.now() - timedelta(days=3)
    Goal.objects.filter(pk=goal.pk).update(created_at=past, updated_at=past)

    logged_in_client.post(
        reverse("goal_edit", args=[goal.pk]), goal_data(title="Learn Django well")
    )

    goal.refresh_from_db()
    assert goal.created_at == past
    assert goal.updated_at > past


def test_ac5_edit_goal_shows_new_values(logged_in_client, goal):
    url = reverse("goal_edit", args=[goal.pk])
    response = logged_in_client.get(url)

    assert response.context["form"]["title"].value() == "Learn Django"

    response = logged_in_client.post(
        url, goal_data(title="Master Django", status="done")
    )

    assert response.status_code == 302
    assert response.url == reverse("goal_list")
    content = logged_in_client.get(reverse("goal_list")).content.decode()
    assert "Master Django" in content
    assert "Learn Django" not in content


def test_ac6_delete_goal_after_confirmation(logged_in_client, goal):
    url = reverse("goal_delete", args=[goal.pk])
    content = logged_in_client.get(reverse("goal_list")).content.decode()

    assert f'hx-post="{url}"' in content
    assert 'hx-confirm="' in content

    response = logged_in_client.get(url)

    assert response.status_code == 405
    assert Goal.objects.filter(pk=goal.pk).exists()

    response = logged_in_client.post(url)

    assert response.status_code == 302
    assert response.url == reverse("goal_list")
    assert not Goal.objects.filter(pk=goal.pk).exists()
    assert (
        "Learn Django"
        not in logged_in_client.get(reverse("goal_list")).content.decode()
    )


@pytest.mark.parametrize("target", ["other", "missing"])
@pytest.mark.parametrize(
    ("method", "name"),
    [
        pytest.param("get", "goal_edit", id="edit_get"),
        pytest.param("post", "goal_edit", id="edit_post"),
        pytest.param("post", "goal_delete", id="delete_post"),
    ],
)
def test_ac8_other_users_goal_is_404(
    logged_in_client, other_goal, method, name, target
):
    pk = other_goal.pk if target == "other" else 999999
    url = reverse(name, args=[pk])

    if method == "get":
        response = logged_in_client.get(url)
    else:
        response = logged_in_client.post(url, goal_data(title="Hijacked"))

    assert response.status_code == 404
    other_goal.refresh_from_db()
    assert other_goal.title == "Learn Rust"


def test_ac27_delete_goal_deletes_its_sessions(logged_in_client, goal, session):
    LearningSession.objects.create(
        goal=goal, date=date(2026, 9, 28), duration_minutes=30
    )

    content = logged_in_client.get(reverse("goal_list")).content.decode()

    assert 'hx-confirm="Delete “Learn Django” and its 2 sessions?"' in content

    logged_in_client.post(reverse("goal_delete", args=[goal.pk]))

    assert LearningSession.objects.filter(goal__pk=goal.pk).count() == 0


def test_ac28_htmx_delete_removes_row(logged_in_client, goal):
    url = reverse("goal_delete", args=[goal.pk])
    content = logged_in_client.get(reverse("goal_list")).content.decode()
    form = re.search(rf'<form[^>]+hx-post="{url}"[^>]*>', content)

    assert form
    assert 'hx-target="closest li"' in form.group(0)
    assert 'hx-swap="outerHTML"' in form.group(0)

    response = logged_in_client.post(url, headers={"HX-Request": "true"})

    assert response.status_code == 200
    assert f'id="goal-{goal.pk}"' not in response.content.decode()
    assert not Goal.objects.filter(pk=goal.pk).exists()


@pytest.fixture
def three_goals(user):
    Goal.objects.create(user=user, title="Plan A", status="planned")
    Goal.objects.create(user=user, title="Doing B", status="in-progress")
    Goal.objects.create(user=user, title="Done C", status="done")


@pytest.mark.parametrize(
    ("status", "shown"),
    [
        pytest.param("planned", "Plan A", id="planned"),
        pytest.param("in-progress", "Doing B", id="in-progress"),
        pytest.param("done", "Done C", id="done"),
    ],
)
def test_ac9_filter_by_status(logged_in_client, three_goals, other_goal, status, shown):
    content = logged_in_client.get(
        reverse("goal_list") + f"?status={status}"
    ).content.decode()

    for title in ["Plan A", "Doing B", "Done C"]:
        assert (title in content) == (title == shown)
    assert "Learn Rust" not in content


def test_ac10_no_filter_shows_all(logged_in_client, three_goals, other_goal):
    content = logged_in_client.get(reverse("goal_list")).content.decode()

    for title in ["Plan A", "Doing B", "Done C"]:
        assert title in content
    assert "Learn Rust" not in content


def test_ac11_empty_states(logged_in_client, user):
    content = logged_in_client.get(reverse("goal_list")).content.decode()

    assert "No goals yet." in content

    Goal.objects.create(user=user, title="Plan A", status="planned")
    content = logged_in_client.get(
        reverse("goal_list") + "?status=done"
    ).content.decode()

    assert "No goals with this status." in content
    assert "Plan A" not in content


def test_ac37_unknown_status_shows_all(logged_in_client, three_goals):
    content = logged_in_client.get(
        reverse("goal_list") + "?status=foo"
    ).content.decode()

    for title in ["Plan A", "Doing B", "Done C"]:
        assert title in content


def test_ac38_filter_links_swap_list_in_place(logged_in_client, three_goals):
    content = logged_in_client.get(reverse("goal_list")).content.decode()

    for label in ["All", "Planned", "In progress", "Done"]:
        assert re.search(rf"<a[^>]+hx-get[^>]*>\s*{label}\s*</a>", content)
    planned = re.search(r'<a[^>]+href="\?status=planned"[^>]*>', content)
    assert planned
    assert "hx-get=" in planned.group(0)
    assert 'hx-target="#goal-list"' in planned.group(0)
    assert 'hx-push-url="true"' in planned.group(0)
    assert 'id="goal-list"' in content

    response = logged_in_client.get(
        reverse("goal_list") + "?status=planned", headers={"HX-Request": "true"}
    )

    names = [t.name for t in response.templates]
    assert "learning/_goal_list.html" in names
    assert "base.html" not in names
    content = response.content.decode()
    assert "Plan A" in content
    assert "Doing B" not in content


def row(content, element_id):
    start = content.index(f'id="{element_id}"')
    return content[start : content.index("</li>", start)]


def test_ac35_goal_rows_and_order(logged_in_client, user, goal, session):
    old = Goal.objects.create(user=user, title="Old goal", status="done")
    Goal.objects.filter(pk=old.pk).update(
        created_at=timezone.now() - timedelta(days=10)
    )
    Goal.objects.create(user=user, title="Newest goal")
    Goal.objects.filter(pk=goal.pk).update(
        updated_at=datetime(2026, 9, 30, 12, tzinfo=UTC)
    )
    url = reverse("goal_list")

    content = logged_in_client.get(url).content.decode()

    assert (
        content.index("Newest goal")
        < content.index("Learn Django")
        < content.index("Old goal")
    )
    goal_row = row(content, f"goal-{goal.pk}")
    for text in ["Planned", "1 h 30 min", "30 Sep 2026"]:
        assert text in goal_row
    assert re.search(r"<span>\s*1 session\s*</span>", goal_row)
    old_row = row(content, f"goal-{old.pk}")
    assert re.search(r"<span>\s*0 sessions\s*</span>", old_row)
    assert "0 min" in old_row

    content = logged_in_client.get(url + "?order=oldest").content.decode()

    assert (
        content.index("Old goal")
        < content.index("Learn Django")
        < content.index("Newest goal")
    )

    content = logged_in_client.get(url + "?order=oldest&status=done").content.decode()

    assert "Old goal" in content
    assert "Learn Django" not in content
    toggle = re.search(r"<a[^>]+>\s*Newest first\s*</a>", content)
    assert toggle
    assert "hx-get=" in toggle.group(0)
    assert 'hx-target="#goal-list"' in toggle.group(0)
    assert 'hx-push-url="true"' in toggle.group(0)


@pytest.mark.parametrize(
    ("name", "kind"),
    [
        ("goal_list", None),
        ("goal_create", None),
        ("goal_edit", "goal"),
        ("goal_delete", "goal"),
        ("session_list", None),
        ("session_create", None),
        ("session_edit", "session"),
        ("session_delete", "session"),
    ],
)
def test_ac22_pages_require_login(client, goal, session, name, kind):
    obj = {"goal": goal, "session": session}.get(kind)
    url = reverse(name, args=[obj.pk] if obj else [])

    response = client.get(url)

    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next={url}"


def test_ac43_history_restore_gets_full_page(logged_in_client, goal):
    url = reverse("goal_list") + "?status=planned"

    response = logged_in_client.get(
        url, headers={"HX-Request": "true", "HX-History-Restore-Request": "true"}
    )

    names = [t.name for t in response.templates]
    assert "base.html" in names
    assert "learning/goal_list.html" in names

    response = logged_in_client.get(url, headers={"HX-Request": "true"})

    assert "HX-Request" in response["Vary"]
