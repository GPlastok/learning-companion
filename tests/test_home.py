import re

from django.urls import reverse


def test_ac2_home_page_is_styled_by_tailwind(logged_in_client):
    response = logged_in_client.get("/")

    assert response.status_code == 200
    template_names = [t.name for t in response.templates]
    assert "core/home.html" in template_names
    assert "base.html" in template_names
    content = response.content.decode()
    assert 'href="/static/css/dist/styles.css' in content
    assert re.search(r'<[^>]+class="[^"]+"[^>]*>\s*Learning Companion', content)


def test_ac3_base_template_loads_htmx(logged_in_client):
    response = logged_in_client.get("/")

    assert 'src="/static/django_htmx/htmx-2.min.js"' in response.content.decode()


def test_ac20_home_requires_login(client):
    response = client.get("/")

    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next=/"


def test_ac21_nav_has_logo_and_logout(logged_in_client):
    content = logged_in_client.get("/").content.decode()

    assert "<nav" in content
    assert re.search(
        rf'<a[^>]+href="{reverse("home")}"[^>]*>\s*Learning Companion\s*</a>', content
    )
    assert re.search(
        rf'<form[^>]+action="{reverse("logout")}"[^>]+method="post"', content
    )
    assert f'href="{reverse("profile")}"' in content
