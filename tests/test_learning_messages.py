import pytest
from conftest import goal_data, session_data
from django.urls import reverse

pytestmark = pytest.mark.django_db


def messages_block(content):
    start = content.index('id="messages"')
    return content[start : content.index("</div>", start)]


@pytest.mark.parametrize(
    ("name", "target", "text"),
    [
        pytest.param("goal_create", None, "Goal created.", id="goal_create"),
        pytest.param("goal_edit", "goal", "Goal updated.", id="goal_edit"),
        pytest.param("goal_delete", "goal", "Goal deleted.", id="goal_delete"),
        pytest.param("session_create", None, "Session created.", id="session_create"),
        pytest.param("session_edit", "session", "Session updated.", id="session_edit"),
        pytest.param(
            "session_delete", "session", "Session deleted.", id="session_delete"
        ),
    ],
)
def test_ac39_message_after_each_change(
    logged_in_client, goal, session, name, target, text
):
    obj = {"goal": goal, "session": session}.get(target)
    url = reverse(name, args=[obj.pk] if obj else [])
    data = {}
    if name.startswith("goal") and not name.endswith("delete"):
        data = goal_data()
    elif name.startswith("session") and not name.endswith("delete"):
        data = session_data(goal)

    response = logged_in_client.post(url, data, follow=True)

    assert text in messages_block(response.content.decode())


@pytest.mark.parametrize(
    ("name", "target", "text"),
    [
        pytest.param("goal_delete", "goal", "Goal deleted.", id="goal"),
        pytest.param("session_delete", "session", "Session deleted.", id="session"),
    ],
)
def test_ac39_htmx_delete_shows_message(
    logged_in_client, goal, session, name, target, text
):
    obj = {"goal": goal, "session": session}[target]

    response = logged_in_client.post(
        reverse(name, args=[obj.pk]), headers={"HX-Request": "true"}
    )

    content = response.content.decode()
    assert 'id="messages"' in content
    assert 'hx-swap-oob="true"' in content
    assert text in content
