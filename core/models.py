from django.db import models


class Tag(models.Model):
    """A focus area, maintained by admins; later tickets tag goals and resources too."""

    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name
