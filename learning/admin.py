from typing import ClassVar

from django.contrib import admin
from django.db import models

from learning.models import Goal, LearningSession, Resource


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "status", "updated_at")


@admin.register(LearningSession)
class LearningSessionAdmin(admin.ModelAdmin):
    list_display = ("goal", "date", "duration_minutes")


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "goal", "type", "created_at")
    # Staff input without a scheme gets https://, as in the app's form (D27).
    formfield_overrides: ClassVar = {models.URLField: {"assume_scheme": "https"}}
