from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.decorators.vary import vary_on_headers

from learning.forms import GoalForm, SessionForm
from learning.models import Goal, LearningSession


def _deleted_response(request, list_name):
    # HTMX swaps the row out for an empty body plus the out-of-band messages (D9,
    # D17); a plain POST goes back to the list.
    if request.htmx:
        return render(request, "messages.html", {"oob": True})
    return redirect(list_name)


@login_required
@vary_on_headers("HX-Request")
def goal_list(request):
    goals = Goal.objects.filter(user=request.user).annotate(
        session_count=Count("sessions"),
        total_minutes=Coalesce(Sum("sessions__duration_minutes"), 0),
    )
    # Newest first unless ?order=oldest; any other value means newest (D13).
    order = request.GET.get("order")
    if order == "oldest":
        goals = goals.order_by("created_at")
    else:
        # Meta.ordering doesn't apply once the annotation groups the rows.
        goals = goals.order_by("-created_at")
        order = ""
    # An unknown status is ignored, so the list shows all goals (D11).
    status = request.GET.get("status")
    if status in Goal.Status.values:
        goals = goals.filter(status=status)
    else:
        status = ""
    context = {
        "goals": goals,
        "status": status,
        "status_choices": Goal.Status.choices,
        "order": order,
    }
    # A history restore needs the whole page, not the list alone (D33).
    if request.htmx and not request.htmx.history_restore_request:
        return render(request, "learning/_goal_list.html", context)
    return render(request, "learning/goal_list.html", context)


@login_required
def goal_create(request):
    form = GoalForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.instance.user = request.user
        form.save()
        messages.success(request, "Goal created.")
        return redirect("goal_list")
    return render(request, "learning/goal_form.html", {"form": form})


@login_required
def goal_edit(request, pk):
    # Only the user's own goals: anyone else's, or a missing pk, is 404 (D1).
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    form = GoalForm(request.POST or None, instance=goal)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Goal updated.")
        return redirect("goal_list")
    return render(request, "learning/goal_form.html", {"form": form})


@login_required
@require_POST
def goal_delete(request, pk):
    # The browser's hx-confirm popup is the confirmation step; no page (D9).
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    goal.delete()
    messages.success(request, "Goal deleted.")
    return _deleted_response(request, "goal_list")


@login_required
@vary_on_headers("HX-Request")
def session_list(request):
    # Sessions belong to the user through their goal (D18).
    sessions = (
        LearningSession.objects.filter(goal__user=request.user)
        .select_related("goal")
        .prefetch_related("tags")
    )
    goals = Goal.objects.filter(user=request.user)
    # A goal that isn't one of the user's is ignored, like an unknown status (D6).
    goal_id = request.GET.get("goal", "")
    if goal_id.isdecimal() and goals.filter(pk=goal_id).exists():
        sessions = sessions.filter(goal__pk=goal_id)
        goal_id = int(goal_id)
    else:
        goal_id = None
    context = {"sessions": sessions, "goals": goals, "goal_id": goal_id}
    if request.htmx and not request.htmx.history_restore_request:
        return render(request, "learning/_session_list.html", context)
    return render(request, "learning/session_list.html", context)


@login_required
def session_create(request):
    if not request.user.goals.exists():
        return render(request, "learning/session_form.html", {"no_goals": True})
    form = SessionForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Session created.")
        return redirect("session_list")
    return render(request, "learning/session_form.html", {"form": form})


@login_required
def session_edit(request, pk):
    session = get_object_or_404(LearningSession, pk=pk, goal__user=request.user)
    form = SessionForm(request.POST or None, instance=session, user=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Session updated.")
        return redirect("session_list")
    return render(request, "learning/session_form.html", {"form": form})


@login_required
@require_POST
def session_delete(request, pk):
    session = get_object_or_404(LearningSession, pk=pk, goal__user=request.user)
    session.delete()
    messages.success(request, "Session deleted.")
    return _deleted_response(request, "session_list")
