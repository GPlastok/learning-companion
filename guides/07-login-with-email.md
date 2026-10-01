# 7. Logging in with email

Out of the box, Django logs people in by username. Decision D5 says they can use their username *or* their email. This chapter shows how Django decides who someone is, and how we changed that.

## Authentication backends

When `LoginView` checks a login, it calls `django.contrib.auth.authenticate(request, username=..., password=...)`. That function asks each **backend** listed in settings, in order, until one returns a user:

```python
# learning_companion/settings.py
AUTHENTICATION_BACKENDS = ["accounts.backends.UsernameOrEmailBackend"]
```

The default is `ModelBackend`, which looks up the username and checks the password. Ours is a subclass that looks in two places.

## The backend

```python
# accounts/backends.py
class UsernameOrEmailBackend(ModelBackend):
    """Log in with the exact username, or with the email in any letter case (D5)."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        user = self._find_user(username)
        if user is None:
            # Hash anyway so a missing user takes as long as a wrong password.
            User().set_password(password)
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def _find_user(self, login):
        for lookup in ({"username": login}, {"email__iexact": login}):
            try:
                return User.objects.get(**lookup)
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                continue
        return None
```

Step by step:

1. The login form's field is still called `username`, but it may hold an email.
2. `_find_user` tries an exact username first, then the email ignoring case. `**lookup` unpacks the dictionary into keyword arguments, so the loop runs `get(username=login)`, then `get(email__iexact=login)`.
3. `check_password` hashes the typed password and compares it with the stored hash. The real password is never stored.
4. `user_can_authenticate` refuses users whose `is_active` is `False`. That's how you block an account without deleting it.
5. Returning `None` means "not me". Django then reports "wrong username or password" without saying which part was wrong.

## Two security details worth learning

### Same speed for every failure

If an unknown username returned at once while a wrong password took 200 ms of hashing, an attacker could time the responses and find out which usernames exist. So for a missing user, the backend hashes the password anyway: `User().set_password(password)`. Django's own `ModelBackend` does the same.

### Ambiguity means no

Usernames and emails are separate fields, so a username *could* look like someone else's email. Sign-up now refuses `@` in usernames (decision D30), and emails are unique at sign-up. The admin could still create duplicates, though. If two accounts share an email, `get()` raises `MultipleObjectsReturned`. The backend then treats it as "no match" rather than guessing which account was meant.

Making email unique in the database itself is a follow-up idea (finding R3).

## Try it yourself

1. With `make dev`, sign up as yourself, log out, and log back in with your email in CAPITAL LETTERS. It works: `email__iexact`.
2. In the shell:

   ```python
   from django.contrib.auth import authenticate
   authenticate(username="you@example.com", password="your password")  # your user
   authenticate(username="you@example.com", password="wrong")          # None
   ```

3. Set your user's `is_active = False` in the shell and save it. Try logging in: refused. Set it back to `True`.
