# 3. The custom user

Ticket #3 asked for "a custom User model". This chapter explains why that's the first thing you do in a Django project, and what migrations are.

## Django already has a user

`django.contrib.auth` ships a `User` model with a username, password, email, first and last name, and flags like `is_staff`. Why replace it?

Because changing it later is painful. Every model that points at the user (profiles, goals, sessions) stores that link in the database. Swapping the user model once those links exist means rewriting the database.

So Django's own docs recommend starting every project with a custom user, even an empty one. Then you can add fields later with a normal migration.

## Our user

```python
# accounts/models.py
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Django's user with no extra fields yet; kept custom so it can change (D2)."""
```

That's it. `AbstractUser` is the full built-in user as a base class, so our `User` has everything the default one has:

| Field | What it holds |
|---|---|
| `id` | the primary key, an integer (decision D3) |
| `username` | unique login name |
| `password` | a hash, never the password itself |
| `email`, `first_name`, `last_name` | profile basics |
| `is_staff`, `is_superuser`, `is_active` | permission flags |
| `date_joined` | when the account was created |
| `last_login` | when they last logged in (decision D4) |

Then one setting tells Django to use it:

```python
# learning_companion/settings.py
AUTH_USER_MODEL = "accounts.User"
```

The format is `"<app label>.<model name>"`.

## Pointing at the user: always use the setting

When another model links to the user, it should never import `User` directly. It uses the setting:

```python
user = models.OneToOneField(settings.AUTH_USER_MODEL, ...)
```

In code that needs the class itself, `django.contrib.auth.get_user_model()` returns it. In tests, the `django_user_model` fixture does the same.

## Migrations

A model is Python. A database has tables. **Migrations** are the bridge: files that describe how to change the tables, step by step.

Two commands:

- `manage.py makemigrations` compares your models with the existing migration files and writes a new file for the difference.
- `manage.py migrate` applies the migrations the database hasn't seen yet, and records each one in a table called `django_migrations`.

After `User` was written, `makemigrations accounts` produced `accounts/migrations/0001_initial.py`. Here's the start of it:

```python
class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, ...)),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ...
```

You almost never write these files by hand. You commit them, so everyone's database ends up the same.

## Why the local database had to go

Your `db.sqlite3` already had Django's built-in migrations applied, including `admin.0001_initial`. That migration links admin log entries to *the user model*, and back then that was `auth.User`.

After switching to `accounts.User`, Django would see `admin.0001` applied before its new dependency `accounts.0001`, and refuse with an "inconsistent migration history" error.

The database was empty (0 users), so the fix was simple (decision D19):

```bash
rm db.sqlite3
make migrate
```

With real data you'd need a careful hand-written migration. That's why the custom user comes first.

## A lint problem with generated code

The project's linter, ruff, flags class attributes that are lists (rule RUF012), because a shared mutable list can surprise you. Django's generated migrations are full of them (`dependencies = [...]`, `operations = [...]`).

Rewriting generated files after every `makemigrations` makes no sense. So `pyproject.toml` switches off just that one rule, just for migration files (decision D29):

```toml
[tool.ruff.lint.per-file-ignores]
"*/migrations/*" = ["RUF012"]
```

## Try it yourself

1. In the shell (`.venv/bin/python manage.py shell`):

   ```python
   from django.contrib.auth import get_user_model
   User = get_user_model()
   User                      # <class 'accounts.models.User'>
   User._meta.db_table       # 'accounts_user'
   ```

2. Run `.venv/bin/python manage.py showmigrations accounts`. Each `[X]` is a migration your database has applied.
3. Add a field to `User`, for example `bio = models.TextField(blank=True)`. Run `.venv/bin/python manage.py makemigrations accounts --dry-run`. Django prints the migration it *would* write. Then undo the change. Don't keep it: it isn't part of any ticket.
