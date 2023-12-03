from django.urls import path
import livesurvey.views as views

urlpatterns = [
    path('<slug:survey_slug>/', views.survey),
    path('<slug:survey_slug>/<str:form_name>/', views.survey_post),

]
