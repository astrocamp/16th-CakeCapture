from django.urls import path
from . import views


app_name = "bonuses"

urlpatterns = [
    path("add/", views.add_bonus, name="add"),
    path("view/", views.view_bonus, name="view"),
]
