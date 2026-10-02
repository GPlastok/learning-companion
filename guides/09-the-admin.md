# 9. The admin

Django's admin is a complete back office: list, search, add, edit and delete rows of any model you register. You write almost no code for it. Decision D18 registers all four models, so you can maintain cohorts and tags and see every profile.

## Registering models

```python
# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import Cohort, Profile, User

admin.site.register(User, UserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "cohort")


@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
```

```python
# core/admin.py
admin.site.register(Tag)
```

There are two ways to register:

- `admin.site.register(Model)`, or `register(Model, SomeAdmin)` with options.
- The `@admin.register(Model)` decorator on a `ModelAdmin` class. Same result, and the options sit right under it.

`list_display` picks the columns of the list page. Without it you get one column, the `__str__` text.

`UserAdmin` is Django's ready-made admin for users. It handles passwords properly: it shows the hash, not the password, and gives you a "change password" form. It works with our custom `User` because that inherits from `AbstractUser`.

## Who can get in

Only users with `is_staff = True` can log in at `/admin/`. A **superuser** (`is_superuser = True`) may do everything. Other staff need permissions assigned in the admin itself.

Create your first admin account:

```bash
.venv/bin/python manage.py createsuperuser
```

It gets a profile automatically, thanks to the signal from chapter 4.

## Things the admin does for you

- Deleting a cohort that profiles use is refused, with a list of what's in the way. That's `on_delete=PROTECT`.
- Deleting a user shows a confirmation page listing everything that goes with it, including the profile (`CASCADE`).
- Unchecking `is_active` on a cohort removes it from the profile form's choices at once.

## Try it yourself

1. Run `createsuperuser`, start `make dev` and open http://127.0.0.1:8000/admin/.
2. Under Accounts → Cohorts, add "Cohort 4". Log in as a user without a cohort and open the profile form: Cohort 4 is offered.
3. Untick "Is active" on Cohort 4 and reload the profile form: it's gone.
4. Add `search_fields = ("user__username", "user__email")` to `ProfileAdmin`, reload, and a search box appears. Remove it again afterwards: it isn't part of a ticket.
