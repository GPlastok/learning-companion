import re

import pytest
from django.urls import reverse

from accounts.models import Profile

pytestmark = pytest.mark.django_db


def test_ac19_delete_asks_first(logged_in_client, user, django_user_model):
    response = logged_in_client.get(reverse("account_delete"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "Are you sure? Deleting profiles is permanent" in content
    assert re.search(
        r'<form method="post"[^>]*>(?:(?!</form>)[\s\S])*Delete my account', content
    )
    assert django_user_model.objects.filter(pk=user.pk).exists()


def test_ac19_delete_removes_user_and_profile(
    logged_in_client, user, django_user_model
):
    response = logged_in_client.post(reverse("account_delete"), follow=True)

    assert response.redirect_chain[-1][0] == reverse("login")
    assert not response.wsgi_request.user.is_authenticated
    assert not django_user_model.objects.filter(pk=user.pk).exists()
    assert not Profile.objects.filter(user__pk=user.pk).exists()


def test_ac19_delete_requires_login(client):
    response = client.get(reverse("account_delete"))

    assert response.status_code == 302
    assert response.url.startswith(reverse("login"))
