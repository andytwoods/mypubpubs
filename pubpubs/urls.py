from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('banana/', admin.site.urls),
    path('accounts/', include('mailauth.urls')),
    path('', include('group.urls')),
    path('', include('users.urls')),
    path('', include('graffiti.urls')),
    path('hijack/', include('hijack.urls')),
    path('accounts/profile/', lambda request: redirect('home', permanent=True)),
    path('captcha/', include('captcha.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += [
        # ...
        path('__debug__/', include('debug_toolbar.urls')),
    ]
