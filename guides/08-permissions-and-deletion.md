# 8. Permissions and deleting an account

Being logged in isn't the same as being allowed. This chapter covers who may see a profile, and how deleting an account works safely.

## Who may see a profile

Decision D13: a profile page is visible to its owner and to staff. Everyone else gets **403 Forbidden**.

```python
# accounts/views.py
@login_required
def profile_detail(request, pk):
    # Check before the lookup, so a 404 never reveals which user ids exist (D31).
    if request.user.pk != pk and not request.user.is_staff:
        raise PermissionDenied
    if request.user.pk == pk:
        profile = profile_for(request.user)
    else:
        profile = get_object_or_404(Profile, user__pk=pk)
    ...
```

Three layers, in order:

1. `@login_required`: anonymous visitors go to the login page (criterion AC4).
2. The permission check: not you and not staff means `PermissionDenied`. Django turns that exception into a 403 response.
3. The lookup: `get_object_or_404` returns the profile, or raises `Http404` if there's none.

## Why the order matters

The first version did the lookup first, then the permission check. That gave a stranger:

- **404** for an id that doesn't exist;
- **403** for an id that does.

By trying `/profile/1/`, `/profile/2/`, … anyone logged in could map out which user ids exist. Review round 1 found it (R4). Now a stranger gets 403 for every id, and only staff ever see a 404 (decision D31).

The general lesson: check permission before you reveal anything, including whether something exists.

## Deleting an account

Decision D12: deleting asks first, and only a POST deletes.

```python
@login_required
def account_delete(request):
    if request.method == "POST":
        user = request.user
        logout(request)
        user.delete()
        return redirect("login")
    return render(request, "accounts/account_confirm_delete.html")
```

- **GET** shows the confirmation page: "Are you sure? Deleting profiles is permanent", with a red button inside a POST form.
- **POST** does the deletion.

### Why GET must never delete

Browsers, link previews and some extensions open links in the background. If a plain link deleted accounts, a preview could delete one. The rule: GET reads, POST (and friends) change things. The CSRF token from chapter 5 then makes sure the POST came from our own page.

### The order inside the POST

1. Keep a reference to the user: `user = request.user`.
2. `logout(request)` clears the session, and `request.user` becomes anonymous.
3. `user.delete()` removes the row. `on_delete=CASCADE` on `Profile.user` removes the profile with it (chapter 4).
4. Redirect to the login page.

## Try it yourself

1. With `make dev`, create two accounts (two browsers, or one private window). Note the second one's id from its profile URL. As the first user, open `/profile/<that id>/`: 403. Then open `/profile/99999/`: also 403.
2. Make the first user staff in the shell (`u.is_staff = True; u.save()`) and open both URLs again: the real profile is 200, the missing one is 404.
3. Delete the second account through its Delete link. In the shell, `Profile.objects.filter(user__username="...").exists()` is now `False`.
