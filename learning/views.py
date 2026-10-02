from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.vary import vary_on_headers
from django_htmx.http import HttpResponseClientRedirect

from learning.forms import GoalForm, ResourceForm, SessionForm
from learning.models import Goal, LearningSession, Resource


def _deleted_response(request, list_name):
    # HTMX swaps the row out for an empty body plus the out-of-band messages (D9,
    # D17); a plain POST goes back to the list.
    if request.htmx:
        return render(request, "messages.html", {"oob": True})
    return redirect(list_name)


def _goals_with_totals(user):
    # The session count and total time, shared by the list and the detail page (D22).
    return Goal.objects.filter(user=user).annotate(
        session_count=Count("sessions"),
        total_minutes=Coalesce(Sum("sessions__duration_minutes"), 0),
    )


@login_required
@vary_on_headers("HX-Request")
def goal_list(request):
    goals = _goals_with_totals(request.user)
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


def _render_goal_detail(request, goal, form):
    context = {
        "goal": goal,
        "resources": goal.resources.prefetch_related("tags"),
        "form": form,
    }
    return render(request, "learning/goal_detail.html", context)


@login_required
def goal_detail(request, pk):
    goal = get_object_or_404(_goals_with_totals(request.user), pk=pk)
    return _render_goal_detail(request, goal, ResourceForm())


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
    # From the detail page there's no row to swap, so the browser goes to the list (D19).
    if request.htmx and request.POST.get("from") == "detail":
        return HttpResponseClientRedirect(reverse("goal_list"))
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


@login_required
@require_POST
def resource_create(request, pk):
    goal = get_object_or_404(_goals_with_totals(request.user), pk=pk)
    form = ResourceForm(request.POST)
    if form.is_valid():
        form.instance.goal = goal
        form.save()
        messages.success(request, "Resource added.")
        return redirect("goal_detail", pk=goal.pk)
    # An invalid post shows the detail page again with the errors (D11).
    return _render_goal_detail(request, goal, form)


@login_required
def resource_edit(request, pk):
    # A resource belongs to the user through its goal (D18).
    resource = get_object_or_404(Resource, pk=pk, goal__user=request.user)
    form = ResourceForm(request.POST or None, instance=resource)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Resource updated.")
        return redirect("goal_detail", pk=resource.goal_id)
    context = {"form": form, "resource": resource}
    return render(request, "learning/resource_form.html", context)


@login_required
@require_POST
def resource_delete(request, pk):
    resource = get_object_or_404(Resource, pk=pk, goal__user=request.user)
    goal_pk = resource.goal_id
    resource.delete()
    messages.success(request, "Resource deleted.")
    # Without HTMX the browser goes back to the goal's page (D13).
    return _deleted_response(request, reverse("goal_detail", args=[goal_pk]))
