# 4. Models and relationships

A model is a Python class that Django turns into a database table. This chapter covers the three models from ticket #3 and the three ways models link to each other.

## The models

```text
User ──1:1── Profile ──many:1── Cohort
                │
                └──many:many── Tag
```

- Each **User** has exactly one **Profile**.
- Many profiles belong to one **Cohort**.
- A profile has many **Tags** (its focus areas), and a tag belongs to many profiles.

## A simple model: `Cohort`

```python
# accounts/models.py
class Cohort(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name
```

Line by line:

- `models.Model` makes it a table, `accounts_cohort`. Django adds an `id` column on its own.
- `CharField(max_length=50, unique=True)`: text up to 50 characters, and the database refuses two cohorts with the same name.
- `BooleanField(default=True)`: new cohorts start active. An admin can switch one off, and inactive cohorts disappear from the profile form (decision D9).
- `Meta.ordering`: queries come back sorted by name unless you ask otherwise. (It's a tuple, not a list, which keeps ruff's RUF012 rule quiet.)
- `__str__`: what you see when the object is printed, for example in the admin or in a template. Without it you'd see `Cohort object (1)`.

`Tag` in `core/models.py` has the same shape. It lives in `core` because later tickets will tag goals and resources too (decision D1).

## The profile, with all three relationships

```python
class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    # Empty until the user completes the profile; then only an admin changes it (D9).
    cohort = models.ForeignKey(Cohort, on_delete=models.PROTECT, null=True, blank=True)
    focus_areas = models.ManyToManyField("core.Tag", blank=True)
```

### One-to-one: `user`

`OneToOneField` is a link where each side has at most one partner. The database stores a `user_id` column with a unique constraint.

`related_name="profile"` names the way back. Given a user, `user.profile` is their profile. Given a profile, `profile.user` is the user.

`on_delete=models.CASCADE`: when the user is deleted, the profile is deleted too. That's how account deletion removes everything (chapter 8).

### Many-to-one: `cohort`

`ForeignKey` means many profiles can point at the same cohort. The database stores a `cohort_id` column.

- `null=True` lets the database column be empty. A new user has no cohort yet.
- `blank=True` lets forms leave it empty. `null` is about the database, `blank` is about validation.
- `on_delete=models.PROTECT`: Django refuses to delete a cohort that profiles still use. Deleting "Cohort 2" by accident would otherwise wipe or orphan its students.

From the other side, `cohort.profile_set.all()` gives every profile in that cohort.

### Many-to-many: `focus_areas`

`ManyToManyField` needs a third table, which Django creates for you (`accounts_profile_focus_areas`), with one row per profile-tag pair.

The model is named as a string, `"core.Tag"`. That's how you point at a model in another app without importing it.

You work with it like a set:

```python
profile.focus_areas.all()        # the tags
profile.focus_areas.add(tag)     # add one
profile.focus_areas.set([a, b])  # replace all
```

CLAUDE.md chose a `Tag` model over a PostgreSQL array column, so that "how many people focus on Python?" works on SQLite and PostgreSQL alike.

## Querying

Every model gets a manager, `objects`, for queries:

```python
Cohort.objects.all()
Cohort.objects.filter(is_active=True)
Cohort.objects.get(name="Cohort 1")             # exactly one, or an exception
User.objects.filter(email__iexact="ADA@example.com")
Profile.objects.filter(user__pk=5)
```

The double underscore means two things:

- a **lookup**: `email__iexact` is "email equals this, ignoring case";
- a **join**: `user__pk` follows the `user` link and compares its `pk`.

## Seed data: data migrations

The cohorts and tags must exist on every database, including the test database. So they're created by migrations, not by hand.

`makemigrations accounts --empty --name seed_cohorts` produced an empty file, which was then filled in:

```python
# accounts/migrations/0003_seed_cohorts.py
STARTING_COHORTS = ["Cohort 1", "Cohort 2", "Cohort 3"]


def create_cohorts(apps, schema_editor):
    Cohort = apps.get_model("accounts", "Cohort")
    Cohort.objects.bulk_create(Cohort(name=name) for name in STARTING_COHORTS)


def delete_cohorts(apps, schema_editor):
    Cohort = apps.get_model("accounts", "Cohort")
    Cohort.objects.filter(name__in=STARTING_COHORTS).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_cohort_profile"),
    ]

    operations = [
        migrations.RunPython(create_cohorts, delete_cohorts),
    ]
```

Two details matter here:

- `apps.get_model(...)` instead of `from accounts.models import Cohort`. A migration must use the model *as it was at that point in history*. If `Cohort` gains a field next year, this old migration still has to run on a fresh database.
- The second function undoes the first. `migrate accounts 0002` runs it to roll back.

`core/migrations/0002_seed_tags.py` does the same for the 21 starting tags.

## Signals: a profile for every user

Every user must have a profile (decision D7), however the user was created: through sign-up, the admin, or `createsuperuser`. Doing it in the sign-up view would miss the other two.

A **signal** is Django's "tell me when this happens" hook. `post_save` fires after any model is saved:

```python
# accounts/signals.py
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Give every new user an empty profile, however the user was made (D7)."""
    # loaddata saves with raw=True and brings its own profiles.
    if created and not kwargs.get("raw"):
        Profile.objects.create(user=instance)
```

- `sender=User`: only for users.
- `created`: `True` on the first save, `False` on later saves. Without this check, every save would try to create another profile.
- `raw`: set when `manage.py loaddata` restores a backup. The backup has its own profile rows, so creating one here would clash (review finding R9).

A receiver only works once its module is imported. The app's config does that when Django starts:

```python
# accounts/apps.py
class AccountsConfig(AppConfig):
    ...
    def ready(self):
        from accounts import signals  # noqa: F401
```

## When the profile is missing anyway

A profile can still go missing: an admin deletes one, or a backup without profiles is loaded. Then `request.user.profile` would raise an exception and the page would crash.

Since every user should have a profile, a missing one is recreated empty, which works as a "reset profile" (decision D34):

```python
def profile_for(user):
    """The user's profile, recreated empty if it went missing (D34)."""
    return Profile.objects.get_or_create(user=user)[0]
```

`get_or_create` returns a pair, `(object, created)`. The `[0]` keeps the object. The views use `profile_for(request.user)` instead of `request.user.profile`.

## Try it yourself

In `.venv/bin/python manage.py shell`:

```python
from accounts.models import Cohort, Profile, User
from core.models import Tag

Cohort.objects.all()                          # the three seeded cohorts
u = User.objects.create_user("test1", password="x")
u.profile                                     # the signal made it
u.profile.cohort = Cohort.objects.first()
u.profile.save()
u.profile.focus_areas.set(Tag.objects.filter(name__in=["Python", "Git"]))
u.profile.focus_areas.all()
Cohort.objects.first().delete()               # ProtectedError: PROTECT at work
u.delete()                                    # the profile goes too: CASCADE
Profile.objects.filter(user__username="test1").exists()   # False
```
