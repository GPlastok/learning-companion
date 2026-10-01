import re


def test_ac2_home_page_is_styled_by_tailwind(client):
    response = client.get("/")

    assert response.status_code == 200
    template_names = [t.name for t in response.templates]
    assert "core/home.html" in template_names
    assert "base.html" in template_names
    content = response.content.decode()
    assert 'href="/static/css/dist/styles.css' in content
    assert re.search(r'<[^>]+class="[^"]+"[^>]*>\s*Learning Companion', content)


def test_ac3_base_template_loads_htmx(client):
    response = client.get("/")

    assert 'src="/static/django_htmx/htmx-2.min.js"' in response.content.decode()
