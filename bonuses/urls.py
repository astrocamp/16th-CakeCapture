from django.urls import path
from . import views


app_name = "bonuses"

urlpatterns = [
    path("view/", views.view_bonus, name="view"),
]
