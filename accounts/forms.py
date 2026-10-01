from django import forms
from django.contrib.auth.forms import UserCreationForm

from accounts.models import Cohort, Profile, User
from core.models import Tag


class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("email", "first_name", "last_name"):
            self.fields[name].required = True

    def clean_username(self):
        # Keep Django's check for usernames that differ only in case.
        username = super().clean_username()
        if username and "@" in username:
            raise forms.ValidationError("Usernames can't contain @.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email


class ProfileForm(forms.ModelForm):
    """Edits the user's names and focus areas; the cohort only while unset (D9, D24)."""

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].initial = self.instance.user.first_name
        self.fields["last_name"].initial = self.instance.user.last_name
        if self.instance.cohort is None:
            self.fields["cohort"] = forms.ModelChoiceField(
                queryset=Cohort.objects.filter(is_active=True)
            )

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
