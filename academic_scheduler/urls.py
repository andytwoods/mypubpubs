from django.urls import path
import academic_scheduler.views as views

urlpatterns = [
    path('', views.form),

]
