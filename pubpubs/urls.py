
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('banana/', admin.site.urls),
    path('accounts/', include('mailauth.urls')),
    path('', include('group.urls')),
    path('', include('users.urls')),
    path('hijack/', include('hijack.urls')),
    path('accounts/profile/', lambda request: redirect('home', permanent=True)),
    path('captcha/', include('captcha.urls')),
]
