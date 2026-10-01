# 5. URLs, views and templates

This chapter follows one request through Django: someone opens `/profile/`.

## The path of a request

```text
browser ──GET /profile/──▶ middleware ──▶ URL list ──▶ view ──▶ template ──▶ HTML
```

1. **Middleware** runs first. Among other things, it loads the session and sets `request.user` to the logged-in user, or to an anonymous user.
2. The **URL list** finds the view that matches the path.
3. The **view** is a Python function that receives the request and returns a response.
4. Usually the view renders a **template**: HTML with placeholders.

## URLs

The project's root list includes the accounts app's list:

```python
# learning_companion/urls.py
urlpatterns = [
    path("", views.home, name="home"),
    path("admin/", admin.site.urls),
    path("", include("accounts.urls")),
]
```

`include("accounts.urls")` at `""` means "also try every pattern in `accounts/urls.py`, as written". Keeping each app's routes in the app is the usual Django layout.

```python
# accounts/urls.py
urlpatterns = [
    path("accounts/signup/", views.signup, name="signup"),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(redirect_authenticated_user=True),
        name="login",
    ),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/delete/", views.account_delete, name="account_delete"),
    path("profile/", views.profile, name="profile"),
    path("profile/<int:pk>/", views.profile_detail, name="profile_detail"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
]
```

- `<int:pk>` captures a number from the URL and passes it to the view as `pk`. `/profile/7/` calls `profile_detail(request, pk=7)`. `/profile/abc/` doesn't match at all.
- `name=` gives each route a name, so code never hard-codes a path.

### Names instead of paths

In Python, `reverse("profile_detail", args=[7])` gives `/profile/7/`. In templates, `{% url 'profile_detail' 7 %}` does the same. `redirect("home")` accepts a name directly.

If a path changes one day, only `urls.py` changes. Every link follows.

## Function views

```python
# accounts/views.py
@login_required
def profile(request):
    return redirect("profile_detail", pk=request.user.pk)
```

A view takes `request` and returns a response. This one returns a redirect to the user's own profile page (criterion AC15).

### `@login_required`

The decorator wraps the view. If the visitor isn't logged in, they never reach the function. They're redirected to the login page instead, with the page they wanted in `?next=`:

```text
/accounts/login/?next=/profile/
```

After logging in, Django sends them back to `next`. Where "the login page" is comes from a setting:

```python
LOGIN_URL = "login"           # a URL name
LOGIN_REDIRECT_URL = "home"   # after login, when there's no ?next=
LOGOUT_REDIRECT_URL = "login" # after logout
```

`home` has `@login_required` too, so the login page is effectively the site's front door (decisions D14, D16).

### Rendering a template

```python
@login_required
def profile_detail(request, pk):
    ...
    return render(
        request,
        "accounts/profile_detail.html",
        {"profile": profile, "is_owner": request.user.pk == pk},
    )
```

`render` fills the template with the **context**, a dictionary of names. Inside the template, `profile` and `is_owner` are now available. Chapter 8 covers the permission check that comes first.

## Class-based views: login and logout

Django ships ready-made views for login and logout, written as classes. `.as_view()` turns a class into a function the URL list can use:

```python
auth_views.LoginView.as_view(redirect_authenticated_user=True)
```

- `LoginView` shows a form, checks the password, logs the user in and redirects. It looks for its template at `registration/login.html`, which is why ours lives at `accounts/templates/registration/login.html`.
- `redirect_authenticated_user=True` sends someone who's already logged in straight to home, so they never see a pointless login form (decision D33).
- `LogoutView` accepts only POST since Django 5.0. A plain link would be a GET, so logout has to be a form with a button (decision D17).

## Templates

### Inheritance

`theme/templates/base.html` is the frame of every page. It defines a hole:

```html
<div class="container mx-auto">
    {% block content %}{% endblock %}
</div>
```

Each page extends the frame and fills the hole:

```html
{% extends "base.html" %}

{% block content %}
<section class="py-16 max-w-xl">
    <h1 class="text-3xl font-bold">{{ profile.user.get_full_name }}</h1>
    ...
{% endblock %}
```

### Template language basics

From `accounts/templates/accounts/profile_detail.html`:

```html
<dd>{{ profile.cohort|default:"Not set" }}</dd>

{% for tag in profile.focus_areas.all %}
<li>{{ tag.name }}</li>
{% empty %}
<li>No focus areas yet</li>
{% endfor %}

{% if is_owner %}
<a href="{% url 'profile_edit' %}">Edit profile</a>
{% endif %}
```

- `{{ ... }}` prints a value. Dots follow attributes, and methods without arguments get called: `profile.focus_areas.all`, no brackets.
- `|default:"Not set"` is a **filter**: if the value is empty, show this instead. The cohort prints through its `__str__`.
- `{% for %} ... {% empty %}` handles the empty list in the same block (criterion AC7).
- `{% url %}` builds links from route names.

Django escapes every `{{ }}` value, so a user named `<script>` shows up as text and never runs. That protects you from cross-site scripting.

### `user` in every template

The nav in `base.html` uses `user` without any view passing it:

```html
<nav class="bg-white border-b">
    <div class="container mx-auto flex items-center justify-between py-4">
        <a href="{% url 'home' %}" class="text-xl font-bold">Learning Companion</a>
        {% if user.is_authenticated %}
        <div class="flex items-center gap-4">
            <a href="{% url 'profile' %}" class="underline">Profile</a>
            <form action="{% url 'logout' %}" method="post">
                {% csrf_token %}
                <button type="submit" class="px-3 py-1 border rounded">Log out</button>
            </form>
        </div>
        {% endif %}
    </div>
</nav>
```

The `auth` **context processor** in `TEMPLATES` settings adds `user` to every template. The logo shows for everyone. The Profile link and Log out appear only for logged-in users (decision D32).

### `{% csrf_token %}`

Every POST form needs it. It adds a hidden secret field. `CsrfViewMiddleware` rejects any POST without the right value, with a 403.

That stops cross-site request forgery: another website can't make your browser submit a form to this site, because it can't read the secret.

## Try it yourself

1. Start `make dev`. Open http://127.0.0.1:8000/profile/ in a private window. The address bar shows `/accounts/login/?next=/profile/`. That's `@login_required`.
2. In the shell:

   ```python
   from django.urls import reverse, resolve
   reverse("profile_detail", args=[3])     # '/profile/3/'
   resolve("/profile/3/").func             # the profile_detail function
   resolve("/profile/3/").kwargs           # {'pk': 3}
   ```

3. Remove `{% csrf_token %}` from the logout form in `base.html`, log in, and click Log out. You get "403 Forbidden, CSRF verification failed". Put it back.
