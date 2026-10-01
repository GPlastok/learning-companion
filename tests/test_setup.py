from django.conf import settings


def test_ac8_suite_runs_against_project():
    assert settings.ROOT_URLCONF == "learning_companion.urls"
    assert "core" in settings.INSTALLED_APPS
