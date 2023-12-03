import inspect

import django.forms
from django import forms
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

from livesurvey.models import Survey, Participant

from . import forms as livesurvey_forms


# Create your views here.

def survey(request, survey_slug):
    # my_survey: Survey = Survey.objects.get(slug=survey_slug)
    if request.POST:
        print(123)

    forms = [cls for name, cls in inspect.getmembers(livesurvey_forms, inspect.isclass)
             if issubclass(cls, django.forms.Form)]

    return render(request, 'livesurvey/livesurvey.html', context={'forms': forms})

def survey_post(request, survey_slug, form_name):
    # below should never be None as POST (and first generated on GET)
    session_id = request.session.session_key
    print(survey_slug, form_name)
    # Participant.update_row(session_id, my_survey, request.POST)

    # needs to return htmx partial
    return HttpResponse('hi')

