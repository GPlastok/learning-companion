from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import Profile, User


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Give every new user an empty profile, however the user was made (D7)."""
    # loaddata saves with raw=True and brings its own profiles.
    if created and not kwargs.get("raw"):
        Profile.objects.create(user=instance)
