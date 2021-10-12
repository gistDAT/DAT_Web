from django.urls import path

from subapp.views import sub_view

app_name = "subapp"

urlpatterns = [
    path('home/', sub_view, name='sub'),
]
