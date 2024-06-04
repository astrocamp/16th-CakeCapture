from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Bonus


@login_required
def view_bonus(request):
    bonus_points = (
        Bonus.objects.filter(user=request.user).order_by("-earned_at").first()
    )
    return render(request, "bonuses/view.html", {"bonus_points": bonus_points})
