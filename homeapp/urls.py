from django.urls import path, include

from homeapp.views import home_view

app_name = "homeapp"

urlpatterns = [
    path('main/', home_view, name='home'),
]
