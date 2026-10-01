from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Django's user with no extra fields yet; kept custom so it can change (D2)."""


class Cohort(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    # Empty until the user completes the profile; then only an admin changes it (D9).
    cohort = models.ForeignKey(Cohort, on_delete=models.PROTECT, null=True, blank=True)
    focus_areas = models.ManyToManyField("core.Tag", blank=True)

    class Meta:
        ordering = ("user__username",)

    def __str__(self):
        return self.user.username


def profile_for(user):
    """The user's profile, recreated empty if it went missing (D34)."""
    return Profile.objects.get_or_create(user=user)[0]
