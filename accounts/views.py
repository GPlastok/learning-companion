from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from accounts.forms import ProfileForm, SignUpForm
from accounts.models import Profile, profile_for


def signup(request):
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("home")
    return render(request, "accounts/signup.html", {"form": form})


@login_required
def profile(request):
    return redirect("profile_detail", pk=request.user.pk)


@login_required
def profile_detail(request, pk):
    # Check before the lookup, so a 404 never reveals which user ids exist (D31).
    if request.user.pk != pk and not request.user.is_staff:
        raise PermissionDenied
    if request.user.pk == pk:
        profile = profile_for(request.user)
    else:
        profile = get_object_or_404(Profile, user__pk=pk)
    return render(
        request,
        "accounts/profile_detail.html",
        {"profile": profile, "is_owner": request.user.pk == pk},
    )


@login_required
def profile_edit(request):
    form = ProfileForm(request.POST or None, instance=profile_for(request.user))
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("profile")
    return render(request, "accounts/profile_form.html", {"form": form})


@login_required
def account_delete(request):
    if request.method == "POST":
        user = request.user
        logout(request)
        user.delete()
        return redirect("login")
    return render(request, "accounts/account_confirm_delete.html")
