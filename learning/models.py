from django.conf import settings
from django.db import models


class Goal(models.Model):
    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        IN_PROGRESS = "in-progress", "In progress"
        DONE = "done", "Done"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="goals"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PLANNED
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title


class LearningSession(models.Model):
    # No user field: the owner is the goal's user (D18).
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name="sessions")
    date = models.DateField()
    # Entered as hours and minutes, stored as whole minutes (D2).
    duration_minutes = models.PositiveIntegerField()
    notes = models.TextField(blank=True)
    tags = models.ManyToManyField("core.Tag", blank=True)

    class Meta:
        ordering = ("-date", "-pk")

    def __str__(self):
        return f"{self.goal.title} on {self.date}"


class Resource(models.Model):
    class Type(models.TextChoices):
        ARTICLE = "article", "Article"
        VIDEO = "video", "Video"
        REPO = "repo", "Repo"
        DOC = "doc", "Doc"

    # No user field: the owner is the goal's user (D18).
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name="resources")
    url = models.URLField(max_length=500)
    title = models.CharField(max_length=200)
    # No default, so the form starts on the blank choice (D10).
    type = models.CharField(max_length=20, choices=Type.choices)
    tags = models.ManyToManyField("core.Tag", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at", "-pk")

    def __str__(self):
        return self.title
