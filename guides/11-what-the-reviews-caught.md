# 11. What the reviews caught

All tests passed after the first build. Four review rounds still found 12 things. This chapter goes through the most instructive ones, because they're the kind of mistake that's easy to make and hard to spot in your own code.

## Round 1

### R1: a username that looks like an email

A user could sign up with the *username* `ada@example.com`. Login tries usernames first (chapter 7), so the real Ada typing her email would hit the wrong account, and her password would fail.

**Lesson:** when two fields can hold the same kind of value, think about collisions between them.

**Fix:** sign-up refuses `@` in usernames (decision D30).

### R2: a test that couldn't fail

The delete-confirmation test checked for `method="post"` on the page. The nav's logout form is on every page and matches that too. Remove the delete form, and the test still passes.

**Lesson:** shared layout (navs, footers) can satisfy loose text checks. Assert on something only the feature produces.

### R4: 404 versus 403 leaks information

A stranger got 404 for missing profiles and 403 for existing ones. That's enough to list which user ids exist (chapter 8).

**Lesson:** check permission before revealing anything, even existence.

### R7: the plan was wrong, not the code

The plan said the user fixtures get database access from `django_user_model`. They don't: the build found out, and added `db` to the fixtures. The plan's text was corrected so the next reader isn't misled.

**Lesson:** a plan is documentation. Keep it true.

## Round 2

### R8: overriding a method dropped a check

The R1 fix added `clean_username` to the sign-up form, without calling `super()`. `UserCreationForm` already had a `clean_username` that refused `Ada` next to `ada`. Our override replaced it, so `Ada` could sign up again.

The fix for one bug created another. That's why the rework gets reviewed too.

**Lesson:** when you override, find out what the parent did. Call `super()` unless you deliberately replace it.

### R9: signals also fire on `loaddata`

`manage.py loaddata` restores a database dump by saving each row, with `raw=True`. Our `post_save` signal would create an empty profile for each loaded user, and then the dump's own profile row would clash with it.

**Lesson:** signals fire for every save, not only the ones you had in mind.

### R10: the login page for someone already logged in

A logged-in user opening `/accounts/login/` saw a login form with a "Log out" button above it. Your answer reshaped the nav (D32: the logo for everyone, buttons only when logged in) and sent logged-in users from the login page to home (D33).

**Lesson:** reviews also find product questions, not only bugs. Those go to a person.

## Round 3

### R12: a fix with a side effect

R9's fix (skip `raw` saves) meant that a dump without profiles leaves users with no profile, and their pages crashed. The answer, D34, recreates a missing profile empty, which works as a "reset".

You asked whether recreating it contradicts deleting it. In this app a user without a profile is a broken state (D7 says every user has one), and the real way to remove data is deleting the account.

**Lesson:** every fix changes the system. Ask what new states it makes possible.

## Round 4

Clean. The reviewer checked the last two fixes, confirmed each test would fail if its feature broke, and found nothing.

## Left for later

- **R3:** emails are unique only through the sign-up form. The admin and `createsuperuser` can still create duplicates, and the database has no constraint. That's a follow-up idea, not a bug today.
- The round 4 reviewer also noticed: if an admin deactivates every cohort, a user without a cohort can't save their profile form.

## Try it yourself

Open the plan's [Review section](../plans/feature-authentication-and-profile-management-plan.md#review). For R8, find the rework step that fixed it and the test it added. Then read `clean_username` in Django's own code:

```bash
grep -n "def clean_username" -A 16 .venv/lib/python3.12/site-packages/django/contrib/auth/forms.py
```

That's the check our first version accidentally switched off.
