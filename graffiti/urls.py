from django.views.generic import TemplateView

from . import views

from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('livesurvey/', include('livesurvey.urls')),
    path("", views.home, name='graffiti_home'),
    path("<str:vr_id>/", views.upload, name="graffiti_upload"),
    path("<str:vr_id>/img/", views.img, name="graffiti_image"),
    path('banana/', admin.site.urls),
    path('accounts/', include('mailauth.urls')),
    path('hijack/', include('hijack.urls')),
    path('accounts/profile/', lambda request: redirect('home', permanent=True)),
    path('captcha/', include('captcha.urls')),
    path("legal/privacy-policy/", TemplateView.as_view(template_name='graffiti/privacy_policy.html'),
         name='privacy_policy'),
    path("legal/terms-and-conditions/", TemplateView.as_view(template_name='graffiti/terms_and_conditions.html'),
         name='terms_and_conditions'),
    path('academic/scheduler/', include('academic_scheduler.urls')),

]

if settings.DEBUG:
    urlpatterns += [
        # ...
        path('__debug__/', include('debug_toolbar.urls')),
    ]

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
