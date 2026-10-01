from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from accounts.models import profile_for


@login_required
def home(request):
    return render(request, "core/home.html", {"profile": profile_for(request.user)})
