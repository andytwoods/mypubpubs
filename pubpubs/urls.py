from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
import graffiti.views as graffit_views

urlpatterns = [
    path('banana/', admin.site.urls),
    path('accounts/', include('mailauth.urls')),
    path('', include('group.urls')),
    path('', include('users.urls')),
    path('hijack/', include('hijack.urls')),
    path('accounts/profile/', lambda request: redirect('home', permanent=True)),
    path('captcha/', include('captcha.urls')),
    path("gmr/<str:vr_id>/", graffit_views.upload, name="home"),
    path("gmr/<str:vr_id>/img/", graffit_views.img, name="img"),
]

if settings.DEBUG:
    urlpatterns += [
        # ...
        path('__debug__/', include('debug_toolbar.urls')),
    ]

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
