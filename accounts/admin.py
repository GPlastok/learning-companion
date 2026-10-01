from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import Cohort, Profile, User

admin.site.register(User, UserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "cohort")


@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
