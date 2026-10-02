import pytest

from learning.templatetags.learning_extras import duration


@pytest.mark.parametrize(
    ("minutes", "text"),
    [(90, "1 h 30 min"), (45, "45 min"), (120, "2 h"), (0, "0 min")],
)
def test_ac36_duration_format(minutes, text):
    assert duration(minutes) == text
