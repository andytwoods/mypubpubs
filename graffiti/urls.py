from django.urls import path
from django.views.generic import TemplateView

from . import views


from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path("", views.home, name='graffiti_home'),
    path("gmr/<str:vr_id>/", views.upload, name="home"),
    path("gmr/<str:vr_id>/img/", views.img, name="img"),
    path("<str:vr_id>/", views.upload, name="graffiti_upload"),
    path("<str:vr_id>/img/", views.img, name="graffiti_image"),
    path('banana/', admin.site.urls),
    path('accounts/', include('mailauth.urls')),
    path('hijack/', include('hijack.urls')),
    path('accounts/profile/', lambda request: redirect('home', permanent=True)),
    path('captcha/', include('captcha.urls')),
    path("privacy-policy/", TemplateView.as_view(template_name='privacy_policy.html'), name='privacy_policy'),
    path("terms-and-conditions/", TemplateView.as_view(template_name='terms_and_conditions.html'),
         name='terms_and_conditions'),
]

if settings.DEBUG:
    urlpatterns += [
        # ...
        path('__debug__/', include('debug_toolbar.urls')),
    ]

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
