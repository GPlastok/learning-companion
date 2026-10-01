# 6. Forms

A Django form does three jobs: it renders HTML fields, it checks the submitted data, and it hands you clean Python values. This chapter covers the sign-up form and the profile form.

## The pattern every form view follows

```python
# accounts/views.py
def signup(request):
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("home")
    return render(request, "accounts/signup.html", {"form": form})
```

Follow both paths:

- **GET** (first visit): `request.POST` is empty, so the form gets `None` and is **unbound**: no data, no errors. The page shows an empty form.
- **POST** (submitted): the form is **bound** to the data. `is_valid()` runs every check.
  - Valid: save, log the new user in (criterion AC11) and redirect.
  - Invalid: fall through to `render`. The same form now carries its errors, and the template shows them next to the fields (criterion AC2).

Redirecting after a successful POST matters. If the view rendered a page instead, pressing reload would submit the form a second time.

## The sign-up form

```python
# accounts/forms.py
class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name")
```

`UserCreationForm` is Django's own sign-up form. It already has the two password fields, checks they match, runs the password validators from settings, and hashes the password on save. We extend it:

- `Meta.model = User`: build users of *our* model.
- `fields`: which model fields to add to the form, on top of the passwords.

### Making fields required

`email`, `first_name` and `last_name` are optional on the model (`blank=True` in `AbstractUser`). The form tightens that (decision D6):

```python
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("email", "first_name", "last_name"):
            self.fields[name].required = True
```

`self.fields` is a dictionary of the form's fields. You can change them after `super().__init__()` has built them.

### Validation with `clean_<field>`

For each field, Django first runs the field's own checks (required, max length, valid email). Then it calls `clean_<fieldname>()` if the form has one. Whatever that method returns becomes the field's clean value. If it raises `ValidationError`, the message is shown on that field.

```python
    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email
```

`email__iexact` makes `ADA@Example.com` collide with `ada@example.com` (criterion AC9). Email has to be unique because people can log in with it (chapter 7).

### Don't throw away the parent's checks

```python
    def clean_username(self):
        # Keep Django's check for usernames that differ only in case.
        username = super().clean_username()
        if username and "@" in username:
            raise forms.ValidationError("Usernames can't contain @.")
        return username
```

`UserCreationForm` already has a `clean_username`: it rejects `Ada` when `ada` exists. The first version of our method didn't call `super()`, so that check silently vanished. Review round 2 caught it (finding R8; chapter 11).

When you override a method, ask what the parent did, and call it unless you mean to replace it. The parent returns `None` once it has recorded an error, hence the `if username and ...`.

The `@` rule is decision D30. A username that looks like an email could hijack someone's email login (finding R1).

## The profile form: a model form with extras

The profile form edits fields from *two* models: names from `User`, focus areas and cohort from `Profile`.

```python
class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    focus_areas = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Profile
        fields = ("focus_areas",)
```

A `ModelForm` builds its fields from a model and can save an instance of it. Here:

- `Meta.fields = ("focus_areas",)` ties `focus_areas` to the profile.
- `first_name` and `last_name` are plain extra fields. The form doesn't know where they belong, so `save()` handles them by hand.
- `ModelMultipleChoiceField` offers a set of database rows as choices. `CheckboxSelectMultiple` draws them as checkboxes instead of a multi-select box.

### A field that comes and goes

The cohort is picked once, and after that only an admin changes it (decision D9). So the field only exists while the cohort is empty:

```python
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].initial = self.instance.user.first_name
        self.fields["last_name"].initial = self.instance.user.last_name
        if self.instance.cohort is None:
            self.fields["cohort"] = forms.ModelChoiceField(
                queryset=Cohort.objects.filter(is_active=True)
            )
```

- `self.instance` is the profile being edited (the view passes `instance=...`).
- `initial` prefills the name fields with the current names.
- The queryset holds only active cohorts (criterion AC17). `ModelChoiceField` is required by default.

Once the cohort is set, the field doesn't exist. A POST that sneaks in `cohort=2` is ignored, because the form only reads fields it has. The test `test_ac17_cohort_locked_once_set` proves that.

### Saving across two models

```python
    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.user.first_name = self.cleaned_data["first_name"]
        profile.user.last_name = self.cleaned_data["last_name"]
        if "cohort" in self.fields:
            profile.cohort = self.cleaned_data["cohort"]
        if commit:
            profile.user.save()
            profile.save()
            self.save_m2m()
        return profile
```

- `super().save(commit=False)` applies the form's model fields to the profile, but doesn't write to the database yet.
- Then we copy the extra values in.
- `save_m2m()` writes the many-to-many focus areas. A many-to-many link needs the profile row to exist first, so with `commit=False` Django leaves that part for you to call.

## Rendering forms

The templates use `{{ form.as_p }}`: every field as a `<p>` with label, input and errors. The login template places fields one by one instead (`{{ form.username }}`) and shows `{{ form.non_field_errors }}`. Errors that aren't about one field, like "wrong username or password", go there.

## Try it yourself

1. In the shell:

   ```python
   from accounts.forms import SignUpForm
   f = SignUpForm({"username": "a@b", "email": "x@example.com", "first_name": "A",
                   "last_name": "B", "password1": "Sup3r-secret-pw",
                   "password2": "Sup3r-secret-pw"})
   f.is_valid()      # False
   f.errors          # {'username': ["Usernames can't contain @."]}
   ```

2. Change `"a@b"` to `"newperson"` and run `is_valid()` again. `f.cleaned_data` now holds the clean values.
3. With `make dev`, sign up with two different passwords and watch the error appear on the form. Nothing was saved: check with `User.objects.count()` in the shell.
