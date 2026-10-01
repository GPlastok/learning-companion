import pytest
from conftest import signup_data
from django.urls import reverse

from accounts.models import Cohort, Profile
from core.models import Tag

pytestmark = pytest.mark.django_db

STARTING_TAGS = {
    "Python",
    "JavaScript",
    "TypeScript",
    "HTML & CSS",
    "React",
    "Django",
    "Node.js",
    "SQL & Databases",
    "Git",
    "Testing",
    "APIs",
    "Docker & DevOps",
    "Cloud",
    "AI & Machine Learning",
    "Data Analysis",
    "UX Research",
    "UI Design",
    "Figma",
    "Accessibility",
    "Product Management",
    "Agile & Scrum",
}


def test_ac13_every_new_user_has_a_profile(django_user_model):
    user = django_user_model.objects.create_user(username="linus", password="x")

    assert user.profile.cohort is None
    assert user.profile.focus_areas.count() == 0


def test_ac13_home_prompts_until_cohort_set(logged_in_client, user):
    content = logged_in_client.get("/").content.decode()

    assert "Complete your profile" in content
    assert f'href="{reverse("profile_edit")}"' in content

    user.profile.cohort = Cohort.objects.get(name="Cohort 1")
    user.profile.save()
    content = logged_in_client.get("/").content.decode()

    assert "Complete your profile" not in content


def test_ac13_raw_save_creates_no_profile(django_user_model):
    django_user_model(username="loaded").save_base(raw=True)

    assert not Profile.objects.filter(user__username="loaded").exists()


def test_ac14_seed_cohorts_and_tags_exist():
    active = Cohort.objects.filter(is_active=True).order_by("name")

    assert [c.name for c in active] == ["Cohort 1", "Cohort 2", "Cohort 3"]
    assert set(Tag.objects.values_list("name", flat=True)) == STARTING_TAGS


def profile_url(user):
    return reverse("profile_detail", args=[user.pk])


def test_ac15_profile_redirects_to_own(logged_in_client, user):
    response = logged_in_client.get(reverse("profile"))

    assert response.status_code == 302
    assert response.url == profile_url(user)


@pytest.mark.parametrize(
    ("viewer", "status"),
    [
        pytest.param("user", 200, id="owner"),
        pytest.param("other_user", 403, id="other_user"),
        pytest.param("staff_user", 200, id="staff"),
    ],
)
def test_ac16_profile_access(client, user, request, viewer, status):
    client.force_login(request.getfixturevalue(viewer))

    response = client.get(profile_url(user))

    assert response.status_code == status


def test_ac16_missing_profile_is_404(client, staff_user):
    client.force_login(staff_user)

    response = client.get(reverse("profile_detail", args=[999999]))

    assert response.status_code == 404


def test_ac16_non_owner_gets_403_for_missing_profile(logged_in_client):
    response = logged_in_client.get(reverse("profile_detail", args=[999999]))

    assert response.status_code == 403


def test_ac4_anonymous_sees_no_profile_data(client, user):
    response = client.get(profile_url(user))

    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next={profile_url(user)}"
    assert "ada@example.com" not in response.content.decode()


def test_ac7_profile_without_focus_areas(logged_in_client, user):
    response = logged_in_client.get(profile_url(user))

    assert response.status_code == 200
    content = response.content.decode()
    assert "Ada Lovelace" in content
    assert "No focus areas yet" in content


def test_ac1_signup_logout_login_shows_own_profile(client, other_user):
    client.post(reverse("signup"), signup_data())
    client.post(reverse("logout"))
    assert "_auth_user_id" not in client.session
    client.post(
        reverse("login"),
        {"username": "linus", "password": signup_data()["password1"]},
    )

    response = client.get(reverse("profile"), follow=True)

    assert response.status_code == 200
    content = response.content.decode()
    assert "Linus Torvalds" in content
    assert "linus@example.com" in content
    assert "grace" not in content
    assert "grace@example.com" not in content


def test_ac5_logout_hides_profile(logged_in_client, user):
    assert logged_in_client.get(profile_url(user)).status_code == 200

    logged_in_client.post(reverse("logout"))
    response = logged_in_client.get(profile_url(user))

    assert response.status_code == 302
    assert "ada@example.com" not in response.content.decode()


def test_ac17_cohort_choices_are_active_only(logged_in_client):
    Cohort.objects.filter(name="Cohort 3").update(is_active=False)

    response = logged_in_client.get(reverse("profile_edit"))

    choices = response.context["form"].fields["cohort"].queryset
    assert [c.name for c in choices] == ["Cohort 1", "Cohort 2"]


def test_ac17_cohort_required_while_unset(logged_in_client, user):
    response = logged_in_client.post(
        reverse("profile_edit"), {"first_name": "Ada", "last_name": "Lovelace"}
    )

    assert response.status_code == 200
    assert "cohort" in response.context["form"].errors
    user.profile.refresh_from_db()
    assert user.profile.cohort is None


def test_ac17_cohort_locked_once_set(logged_in_client, user):
    user.profile.cohort = Cohort.objects.get(name="Cohort 1")
    user.profile.save()

    response = logged_in_client.get(reverse("profile_edit"))
    assert "cohort" not in response.context["form"].fields

    logged_in_client.post(
        reverse("profile_edit"),
        {
            "first_name": "Ada",
            "last_name": "Lovelace",
            "cohort": Cohort.objects.get(name="Cohort 2").pk,
        },
    )
    user.profile.refresh_from_db()
    assert user.profile.cohort.name == "Cohort 1"


def test_ac18_user_edits_names_and_focus_areas(logged_in_client, user):
    tags = Tag.objects.filter(name__in=["Python", "Testing"])

    response = logged_in_client.post(
        reverse("profile_edit"),
        {
            "first_name": "Augusta",
            "last_name": "King",
            "cohort": Cohort.objects.get(name="Cohort 1").pk,
            "focus_areas": [t.pk for t in tags],
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("profile")
    user.refresh_from_db()
    assert (user.first_name, user.last_name) == ("Augusta", "King")
    assert set(user.profile.focus_areas.values_list("name", flat=True)) == {
        "Python",
        "Testing",
    }


@pytest.mark.parametrize(
    ("name", "with_pk"),
    [
        pytest.param("home", False, id="home"),
        pytest.param("profile_edit", False, id="profile_edit"),
        pytest.param("profile_detail", True, id="profile_detail"),
    ],
)
def test_ac25_missing_profile_is_recreated(logged_in_client, user, name, with_pk):
    url = reverse(name, args=[user.pk] if with_pk else [])
    Profile.objects.filter(user=user).delete()
    user.refresh_from_db()

    response = logged_in_client.get(url)

    assert response.status_code == 200
    assert Profile.objects.get(user=user).cohort is None
