# 10. Testing with pytest-django

64 tests protect this project. This chapter shows how they're built, so you can read any of them and write your own.

## The tools

- **pytest** runs the tests. A test is any function named `test_...` in a file named `test_*.py` under `tests/`.
- **pytest-django** connects pytest to Django: it loads the settings, creates a fresh test database, and provides Django fixtures.

`make test` runs everything. `make test ARGS="-k ac16"` runs the tests whose names contain `ac16`.

## Naming: one criterion, one name

The project rule (CLAUDE.md): a test is named after the acceptance criterion it proves.

```text
test_ac8_login_accepts_username_or_email   →  AC8 in the plan
test_ac19_delete_asks_first                →  AC19
```

So when a test fails, you know at once which promised behaviour broke.

## The database in tests

Tests never touch your `db.sqlite3`. pytest-django builds a separate test database and runs every migration on it, including the seed migrations, so the cohorts and tags exist there too.

A test may only use the database if it asks to. Most test files ask once, at the top:

```python
pytestmark = pytest.mark.django_db
```

Each test runs inside a transaction that is rolled back afterwards. Users created in one test are gone in the next.

## Fixtures: reusable setup

A **fixture** is a function that prepares something. A test receives it by naming it as an argument. Shared fixtures live in `tests/conftest.py`, which pytest loads on its own:

```python
# tests/conftest.py
@pytest.fixture
def user(db, django_user_model, password):
    return django_user_model.objects.create_user(
        username="ada",
        email="ada@example.com",
        password=password,
        first_name="Ada",
        last_name="Lovelace",
    )


@pytest.fixture
def logged_in_client(client, user):
    client.force_login(user)
    return client
```

Fixtures can use other fixtures. `logged_in_client` needs `client` and `user`, `user` needs `db` and `password`, and pytest builds the whole chain.

The ones from pytest-django:

| Fixture | Gives you |
|---|---|
| `db` | database access for this test |
| `client` | a fake browser (Django's test client) |
| `django_user_model` | the user model (`accounts.User`) |
| `admin_client` | a client logged in as a fresh superuser |

`create_user` hashes the password properly. Creating a user with `User(password="...")` would store the plain text, and logging in would fail.

`force_login` logs a client in without a password check. Use it when a test is *about* something else: the profile page, not logging in.

## The test client

The client sends requests to your app without a real server or browser:

```python
def test_ac11_signup_logs_in_and_redirects_home(client):
    response = client.post(reverse("signup"), signup_data(), follow=True)

    assert response.redirect_chain[-1][0] == reverse("home")
    assert response.wsgi_request.user.is_authenticated
```

- `client.get(url)` and `client.post(url, data)` return the response.
- `follow=True` follows redirects. `redirect_chain` lists every hop, so `[-1][0]` is the final URL.
- `response.wsgi_request.user` is the user the request ended as.

And without `follow`:

```python
    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next=/"
```

Other things you can check on a response:

- `response.content.decode()`: the HTML as text;
- `response.templates`: which templates were rendered;
- `response.context["form"]`: the objects the view passed to the template, for example the form with its `errors`.

## One test, many inputs

When one rule is checked against several inputs, it's one test with `parametrize` (a CLAUDE.md rule):

```python
@pytest.mark.parametrize("field", ["first_name", "last_name", "email"])
def test_ac10_signup_requires_names_and_email(client, django_user_model, field):
    response = client.post(reverse("signup"), signup_data(**{field: ""}))

    assert response.status_code == 200
    assert field in response.context["form"].errors
    assert not django_user_model.objects.exists()
```

pytest runs it three times, once per value, and reports each run on its own line. `signup_data(**overrides)` in `conftest.py` returns valid sign-up data with your changes applied, so each row states only what's different.

Rows can also pick fixtures by name:

```python
def test_ac16_profile_access(client, user, request, viewer, status):
    client.force_login(request.getfixturevalue(viewer))
```

`viewer` is `"user"`, `"other_user"` or `"staff_user"`, and `request.getfixturevalue` turns the name into the fixture's value.

## What makes a good assertion

A test is only as good as the assertion that would catch a broken behaviour. Two examples from the reviews (chapter 11):

- `assert 'method="post"' in content` looked like "the delete page has a form". But the nav's logout form matched too, so the test would pass with no delete form at all. It now looks for the form with the "Delete my account" button.
- The sign-up/logout/login walk-through never checked that logout worked. One line fixed that: `assert "_auth_user_id" not in client.session`.

Ask of every test: if I deleted the feature, would this fail?

## Red first

From chapter 1: write the test, watch it fail, then write the code. Here's step 12 from the build log:

```text
Step 12 (R1) red: … 1 failed, `assert 302 == 200` (username with @ accepted), as planned.
Step 12 green: SignUpForm.clean_username. make test … 56 passed.
```

The red run proves the test can see the bug. The green run proves the fix works, and that the other 55 tests still pass.

## Try it yourself

1. Run `make test ARGS="-k ac16 -v"` and read the test ids, like `test_ac16_profile_access[other_user]`.
2. Break something on purpose: in `accounts/views.py`, replace `raise PermissionDenied` with `pass`. Run `make test`. Which tests fail, and do their names tell you what broke? Then undo with `git checkout accounts/views.py`.
3. Write a test of your own in a scratch file, `tests/test_scratch.py`:

   ```python
   import pytest
   from django.urls import reverse

   pytestmark = pytest.mark.django_db


   def test_profile_page_shows_cohort_not_set(logged_in_client, user):
       response = logged_in_client.get(reverse("profile_detail", args=[user.pk]))
       assert "Not set" in response.content.decode()
   ```

   Run it with `make test ARGS="tests/test_scratch.py"`. Then delete the file, since it isn't part of a ticket.
