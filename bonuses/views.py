from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import *


@login_required
def add_bonus(request):
    if request.method == "POST":
        points = int(request.POST.get("points"))
        bonus_point, created = Bonus.objects.get_or_create(user=request.user)
        bonus_point.points += points
        bonus_point.save()
        return redirect("bonus_points")
    return render(request, "bonuses/add_bonus_points.html")


@login_required
def view_bonus(request):
    bonus_points = Bonus.objects.filter(user=request.user).first()
    return render(
        request, "bonuses/view_bonus_points.html", {"bonus_points": bonus_points}
    )
