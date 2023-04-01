from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.MyLoginView.as_view(), name='login'),
    path("privacy-policy/", TemplateView.as_view(template_name='privacy_policy.html'), name='privacy_policy'),
    path("terms-and-conditions/", TemplateView.as_view(template_name='terms_and_conditions.html'), name='terms_and_conditions'),
]
