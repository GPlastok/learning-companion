from django.contrib import admin

from learning.models import Goal, LearningSession


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "status", "updated_at")


@admin.register(LearningSession)
class LearningSessionAdmin(admin.ModelAdmin):
    list_display = ("goal", "date", "duration_minutes")
