
from django.urls import path, include
from django.conf import settings
from group import views

urlpatterns = [
    path('', views.home, name='home'),
    path('group/<uuid:uuid>/', views.group, name='group'),
    path('group/<uuid:uuid>/edit/', views.GroupPrefs.as_view(), name='admin-group-edit'),
    path('group/<uuid:uuid>/add/<str:email>/', views.add_person, name='accept_person')

]

if settings.DEBUG:
    urlpatterns += [
        # ...
        path('__debug__/', include('debug_toolbar.urls')),
    ]