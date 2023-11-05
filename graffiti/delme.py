from django.urls import path
from study import views

urlpatterns = (
   path("study/ethics/", views.ethics, "ethics") # noqa
   path("study/<int:id>/", views.study, "study")
   path("study/new/", # noqa
       views.NewStudy.as_view(),  "new_study") # noqa
)
