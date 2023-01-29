
from django.urls import path

from group import views

urlpatterns = [
    path('group/<uuid:uuid>/', views.group),

]
