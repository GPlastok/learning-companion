import re

import pytest
from conftest import resource_data
from django.urls import reverse

from core.models import Tag
from learning.models import Goal, Resource

pytestmark = pytest.mark.django_db


def detail(client, goal):
    return client.get(reverse("goal_detail", args=[goal.pk])).content.decode()


def test_ac8_resource_shows_title_link_and_type(logged_in_client, goal, resource):
    content = detail(logged_in_client, goal)

    assert re.search(rf'<a href="{resource.url}"[^>]*>Django models docs</a>', content)
    assert '<span class="px-2 border rounded">Doc</span>' in content


def test_ac26_link_opens_in_new_tab(logged_in_client, goal, resource):
    link = re.search(rf'<a href="{resource.url}"[^>]*>', detail(logged_in_client, goal))

    assert link
    assert 'target="_blank"' in link.group(0)
    assert 'rel="noopener noreferrer"' in link.group(0)


def test_ac16_only_this_goals_resources(
    logged_in_client, user, goal, resource, other_resource
):
    sql = Goal.objects.create(user=user, title="Learn SQL")
    Resource.objects.create(
        goal=sql, url="https://sqlbolt.com/", title="SQL tutorial", type="article"
    )

    content = detail(logged_in_client, goal)

    assert "Django models docs" in content
    assert "SQL tutorial" not in content
    assert "The Rust book" not in content


def test_ac17_empty_state(logged_in_client, goal):
    assert "No resources yet." in detail(logged_in_client, goal)


def test_ac24_newest_first(logged_in_client, goal):
    for title in ["Older talk", "Newer talk"]:
        Resource.objects.create(
            goal=goal, url="https://example.com/1", title=title, type="video"
        )

    content = detail(logged_in_client, goal)

    assert content.index("Newer talk") < content.index("Older talk")


def create_url(goal):
    return reverse("resource_create", args=[goal.pk])


def detail_form(client, goal):
    return client.get(reverse("goal_detail", args=[goal.pk])).context["form"]


def test_ac5_detail_has_attach_form(logged_in_client, goal):
    response = logged_in_client.get(reverse("goal_detail", args=[goal.pk]))

    assert {"url", "title", "type"} <= set(response.context["form"].fields)
    assert f'<form method="post" action="{create_url(goal)}"' in (
        response.content.decode()
    )


def test_ac6_type_has_four_choices(logged_in_client, goal):
    form = detail_form(logged_in_client, goal)

    assert [v for v, _ in form.fields["type"].choices if v] == [
        "article",
        "video",
        "repo",
        "doc",
    ]


def test_ac32_type_starts_blank(logged_in_client, goal):
    form = detail_form(logged_in_client, goal)

    assert form.fields["type"].choices[0][0] == ""
    assert not form["type"].value()


def test_ac7_attach_stores_and_shows(logged_in_client, goal):
    assert logged_in_client.get(create_url(goal)).status_code == 405

    response = logged_in_client.post(create_url(goal), resource_data())

    assert response.status_code == 302
    assert response.url == reverse("goal_detail", args=[goal.pk])
    resource = Resource.objects.get(goal=goal)
    assert (resource.url, resource.title, resource.type) == (
        "https://www.youtube.com/watch?v=abc123",
        "Django ORM talk",
        "video",
    )
    assert "Django ORM talk" in detail(logged_in_client, goal)


def test_ac14_reload_does_not_attach_twice(logged_in_client, goal):
    response = logged_in_client.post(create_url(goal), resource_data())

    logged_in_client.get(response.url)
    logged_in_client.get(response.url)

    assert Resource.objects.count() == 1


def test_ac15_message_after_attach(logged_in_client, goal):
    response = logged_in_client.post(create_url(goal), resource_data(), follow=True)

    assert "Resource added." in response.content.decode()


def test_ac34_same_url_twice(logged_in_client, goal):
    logged_in_client.post(create_url(goal), resource_data())
    logged_in_client.post(create_url(goal), resource_data())

    assert Resource.objects.filter(goal=goal).count() == 2


def test_ac31_url_without_scheme_gets_https(logged_in_client, goal):
    logged_in_client.post(create_url(goal), resource_data(url="example.com/post"))

    assert Resource.objects.get(goal=goal).url == "https://example.com/post"


def test_ac31_url_field_is_plain_text(logged_in_client, goal):
    field = re.search(r'<input[^>]+name="url"[^>]*>', detail(logged_in_client, goal))

    assert field
    assert 'type="text"' in field.group(0)
    assert 'inputmode="url"' in field.group(0)
    assert 'type="url"' not in field.group(0)


@pytest.mark.parametrize(
    "value",
    [
        "http://example.com/a",
        "https://example.com/a",
        "ftp://ftp.example.com/file.pdf",
        "ftps://ftp.example.com/file.pdf",
    ],
)
def test_ac39_url_schemes_accepted(logged_in_client, goal, value):
    response = logged_in_client.post(create_url(goal), resource_data(url=value))

    assert response.status_code == 302
    assert Resource.objects.get(goal=goal).url == value


def assert_rejected(response, field):
    assert response.status_code == 200
    assert field in response.context["form"].errors
    assert Resource.objects.count() == 0


@pytest.mark.parametrize(
    "value",
    ["not a url", "javascript:alert(1)", "file:///etc/passwd", "localhost:8000/docs"],
)
def test_ac9_invalid_url_is_rejected(logged_in_client, goal, value):
    response = logged_in_client.post(create_url(goal), resource_data(url=value))

    assert_rejected(response, "url")


def test_ac10_missing_url_is_rejected(logged_in_client, goal):
    response = logged_in_client.post(create_url(goal), resource_data(url=""))

    assert_rejected(response, "url")


def test_ac11_unknown_type_is_rejected(logged_in_client, goal):
    response = logged_in_client.post(create_url(goal), resource_data(type="podcast"))

    assert_rejected(response, "type")


@pytest.mark.parametrize("title", ["", "x" * 201])
def test_ac22_title_rules(logged_in_client, goal, title):
    response = logged_in_client.post(create_url(goal), resource_data(title=title))

    assert_rejected(response, "title")


@pytest.mark.parametrize(("extra", "accepted"), [(480, True), (481, False)])
def test_ac23_url_length(logged_in_client, goal, extra, accepted):
    response = logged_in_client.post(
        create_url(goal), resource_data(url="https://example.com/" + "a" * extra)
    )

    assert Resource.objects.count() == (1 if accepted else 0)
    if not accepted:
        assert "url" in response.context["form"].errors


def test_ac12_rejected_submission_keeps_values(logged_in_client, goal):
    response = logged_in_client.post(
        create_url(goal), resource_data(url="not a url", title="Kept title")
    )

    content = response.content.decode()
    assert 'value="not a url"' in content
    assert 'value="Kept title"' in content


@pytest.mark.parametrize("target", ["other", "missing"])
def test_ac13_attach_to_other_goal_is_404(logged_in_client, other_goal, target):
    pk = other_goal.pk if target == "other" else 999999

    response = logged_in_client.post(
        reverse("resource_create", args=[pk]), resource_data()
    )

    assert response.status_code == 404
    assert Resource.objects.count() == 0


def test_ac35_attach_requires_login(client, goal):
    url = create_url(goal)

    response = client.post(url, resource_data())

    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next={url}"
    assert Resource.objects.count() == 0


def test_ac25_tags_are_saved_and_shown(logged_in_client, goal):
    tags = Tag.objects.filter(name__in=["Python", "Testing"])

    logged_in_client.post(create_url(goal), resource_data(tags=[t.pk for t in tags]))

    resource = Resource.objects.get(goal=goal)
    assert set(resource.tags.values_list("name", flat=True)) == {"Python", "Testing"}
    content = detail(logged_in_client, goal)
    assert re.search(
        rf'<li id="resource-{resource.pk}"[^>]*>(?:(?!</li>).)*Python, Testing',
        content,
        re.DOTALL,
    )


def test_ac25_tags_are_optional(logged_in_client, goal):
    logged_in_client.post(create_url(goal), resource_data())

    resource = Resource.objects.get(goal=goal)
    assert resource.tags.count() == 0


def test_ac27_edit_resource(logged_in_client, goal, resource):
    url = reverse("resource_edit", args=[resource.pk])
    assert f'href="{url}"' in detail(logged_in_client, goal)
    assert logged_in_client.get(url).status_code == 200
    python = Tag.objects.get(name="Python")
    data = resource_data(
        url="https://example.com/new", title="Renamed", type="article", tags=[python.pk]
    )

    response = logged_in_client.post(url, data)

    assert response.status_code == 302
    assert response.url == reverse("goal_detail", args=[goal.pk])
    resource.refresh_from_db()
    assert (resource.url, resource.title, resource.type) == (
        "https://example.com/new",
        "Renamed",
        "article",
    )
    assert list(resource.tags.values_list("name", flat=True)) == ["Python"]
    response = logged_in_client.post(url, data, follow=True)
    assert "Resource updated." in response.content.decode()


def test_ac33_edit_form_has_no_goal_field(logged_in_client, user, goal, resource):
    url = reverse("resource_edit", args=[resource.pk])
    assert "goal" not in logged_in_client.get(url).context["form"].fields
    second = Goal.objects.create(user=user, title="Learn SQL")

    logged_in_client.post(url, resource_data(goal=second.pk))

    resource.refresh_from_db()
    assert resource.goal == goal


@pytest.mark.parametrize("target", ["other", "missing"])
@pytest.mark.parametrize("method", ["get", "post"])
def test_ac29_other_users_resource_edit_is_404(
    logged_in_client, other_resource, method, target
):
    pk = other_resource.pk if target == "other" else 999999
    url = reverse("resource_edit", args=[pk])

    if method == "get":
        response = logged_in_client.get(url)
    else:
        response = logged_in_client.post(url, resource_data(title="Hijacked"))

    assert response.status_code == 404
    other_resource.refresh_from_db()
    assert other_resource.title == "The Rust book"


def test_ac36_edit_requires_login(client, resource):
    url = reverse("resource_edit", args=[resource.pk])

    response = client.get(url)

    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next={url}"


def test_ac28_delete_resource(logged_in_client, goal, resource):
    url = reverse("resource_delete", args=[resource.pk])
    form = re.search(
        rf'<form[^>]+hx-post="{url}"[^>]*>', detail(logged_in_client, goal)
    )

    assert form
    assert 'hx-confirm="Delete “Django models docs”?"' in form.group(0)
    assert 'hx-target="closest li"' in form.group(0)
    assert 'hx-swap="outerHTML"' in form.group(0)

    assert logged_in_client.get(url).status_code == 405
    assert Resource.objects.filter(pk=resource.pk).exists()

    response = logged_in_client.post(url)

    assert response.status_code == 302
    assert response.url == reverse("goal_detail", args=[goal.pk])
    assert not Resource.objects.filter(pk=resource.pk).exists()


def test_ac28_htmx_delete_removes_row(logged_in_client, resource):
    url = reverse("resource_delete", args=[resource.pk])

    response = logged_in_client.post(url, headers={"HX-Request": "true"})

    assert response.status_code == 200
    content = response.content.decode()
    assert 'hx-swap-oob="true"' in content
    assert "Resource deleted." in content
    assert f'id="resource-{resource.pk}"' not in content
    assert not Resource.objects.filter(pk=resource.pk).exists()


@pytest.mark.parametrize("target", ["other", "missing"])
def test_ac38_other_users_resource_delete_is_404(
    logged_in_client, other_resource, target
):
    pk = other_resource.pk if target == "other" else 999999

    response = logged_in_client.post(reverse("resource_delete", args=[pk]))

    assert response.status_code == 404
    assert Resource.objects.filter(pk=other_resource.pk).exists()


def test_ac37_delete_requires_login(client, resource):
    url = reverse("resource_delete", args=[resource.pk])

    response = client.post(url)

    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next={url}"
    assert Resource.objects.filter(pk=resource.pk).exists()
