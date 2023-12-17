from django.urls import path
import livesurvey.views as views

urlpatterns = [
    path('<slug:survey_slug>/', views.survey),

    # note below, purposely leaving off slash
    path('<slug:survey_slug>/<str:form_name>', views.survey_post),

]
