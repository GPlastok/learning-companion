import re

import pytest
from django.urls import reverse

from learning.models import Goal

pytestmark = pytest.mark.django_db


def test_ac1_detail_page_shows_title(logged_in_client, goal):
    response = logged_in_client.get(reverse("goal_detail", args=[goal.pk]))

    assert response.status_code == 200
    assert "Learn Django" in response.content.decode()


def test_ac21_detail_page_shows_goal_fields(logged_in_client, goal, session):
    content = logged_in_client.get(
        reverse("goal_detail", args=[goal.pk])
    ).content.decode()

    assert "Models and views" in content
    assert "Planned" in content
    assert "<span>1 session</span>" in content
    assert "1 h 30 min" in content
    assert f'href="{reverse("goal_edit", args=[goal.pk])}"' in content


@pytest.mark.parametrize("target", ["other", "missing"])
def test_ac3_other_users_goal_detail_is_404(logged_in_client, other_goal, target):
    pk = other_goal.pk if target == "other" else 999999

    response = logged_in_client.get(reverse("goal_detail", args=[pk]))

    assert response.status_code == 404


def test_ac4_detail_page_requires_login(client, goal, password):
    url = reverse("goal_detail", args=[goal.pk])

    response = client.get(url)

    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next={url}"

    response = client.post(response.url, {"username": "ada", "password": password})

    assert response.status_code == 302
    assert response.url == url


def test_ac2_goal_list_links_to_detail(logged_in_client, goal):
    content = logged_in_client.get(reverse("goal_list")).content.decode()

    assert re.search(
        rf'<a href="{reverse("goal_detail", args=[goal.pk])}"[^>]*>Learn Django</a>',
        content,
    )


def test_ac30_delete_goal_from_detail(logged_in_client, goal, session):
    url = reverse("goal_delete", args=[goal.pk])
    content = logged_in_client.get(
        reverse("goal_detail", args=[goal.pk])
    ).content.decode()
    form = re.search(rf'<form[^>]+hx-post="{url}"[^>]*>', content)

    assert form
    assert 'hx-confirm="Delete “Learn Django” and its 1 session?"' in form.group(0)
    assert '<input type="hidden" name="from" value="detail">' in content

    response = logged_in_client.post(
        url, {"from": "detail"}, headers={"HX-Request": "true"}
    )

    assert response.status_code == 200
    assert response["HX-Redirect"] == reverse("goal_list")
    assert not Goal.objects.filter(pk=goal.pk).exists()
    assert (
        "Goal deleted." in logged_in_client.get(reverse("goal_list")).content.decode()
    )


def test_ac30_delete_from_detail_without_htmx(logged_in_client, goal):
    response = logged_in_client.post(
        reverse("goal_delete", args=[goal.pk]), {"from": "detail"}
    )

    assert response.status_code == 302
    assert response.url == reverse("goal_list")


def test_r4_goal_actions_are_in_a_div(logged_in_client, goal):
    content = logged_in_client.get(
        reverse("goal_detail", args=[goal.pk])
    ).content.decode()

    assert re.search(
        rf'<div class="mt-4 flex gap-4">\s*<a href="{reverse("goal_edit", args=[goal.pk])}"',
        content,
    )
