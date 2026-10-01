from django.contrib.auth.backends import ModelBackend

from accounts.models import User


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
