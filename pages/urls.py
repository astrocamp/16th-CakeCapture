from django.urls import path ,include
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('accounts/',include("accounts.urls")),
    path('accounts/', include('allauth.urls')), 
  ]

    # path('accounts/', include('allauth.urls')), 