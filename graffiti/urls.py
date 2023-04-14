from django.urls import path

from . import views

app_name = 'graffiti'
urlpatterns = [
    path("gmr/<str:vr_id>", views.upload, name="home"),
    path("gmr/<str:vr_id>/img", views.img, name="img"),
]
