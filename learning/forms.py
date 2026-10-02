from django import forms
from django.utils import timezone

from core.models import Tag
from learning.models import Goal, LearningSession


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ("title", "description", "status")


class SessionForm(forms.ModelForm):
    """Takes the duration as hours and minutes and stores whole minutes (D2, D27)."""

    # One session is at most 24 hours (D32).
    hours = forms.IntegerField(min_value=0, max_value=24)
    minutes = forms.IntegerField(min_value=0, max_value=59)
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = LearningSession
        fields = ("goal", "date", "notes", "tags")

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["goal"].queryset = Goal.objects.filter(user=user)
        self.fields["date"].initial = timezone.localdate
        self.fields["date"].widget = forms.DateInput(attrs={"type": "date"})
        if self.instance.pk:
            hours, minutes = divmod(self.instance.duration_minutes, 60)
            self.fields["hours"].initial = hours
            self.fields["minutes"].initial = minutes

    def clean_date(self):
        # A session records learning that has started, never a planned one (D3).
        value = self.cleaned_data["date"]
        if value > timezone.localdate():
            raise forms.ValidationError("The date can't be in the future.")
        return value

    def clean(self):
        cleaned = super().clean()
        hours, minutes = cleaned.get("hours"), cleaned.get("minutes")
        if hours is not None and minutes is not None:
            total = hours * 60 + minutes
            if total == 0:
                raise forms.ValidationError("The duration must be more than zero.")
            if total > 24 * 60:
                raise forms.ValidationError("A session can't be longer than 24 hours.")
        return cleaned

    def save(self, commit=True):
        session = super().save(commit=False)
        session.duration_minutes = (
            self.cleaned_data["hours"] * 60 + self.cleaned_data["minutes"]
        )
        if commit:
            session.save()
            self.save_m2m()
        return session
