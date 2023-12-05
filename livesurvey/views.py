from django.http import HttpResponse
from django.shortcuts import render

from livesurvey.models import Survey, Participant
from .forms import DemographicsForm
from .tools import get_livesurvey_forms, get_livesurvey_form


# Create your views here.

def survey(request, survey_slug):
    # my_survey: Survey = Survey.objects.get(slug=survey_slug)
    forms = get_livesurvey_forms()

    return render(request, 'livesurvey/livesurvey.html', context={'forms': forms})


def get_session_id(request):
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key

def survey_post(request, survey_slug, form_name):
    # below should never be None as POST (and first generated on GET)
    my_survey: Survey
    try:
        my_survey = Survey.objects.get(slug=survey_slug)
    except Survey.DoesNotExist:
        if '127.0.0.1' in request.get_host():
            my_survey = Survey(slug=survey_slug, title='local host demo survey autocreated')
            my_survey.save()

    session_id = get_session_id(request)
    form_data = request.POST

    found = get_livesurvey_form(form_name)
    if not found:
        return HttpResponse('There has been an error')
    form_cls = found[0]

    form = form_cls(data=form_data)
    if form.is_valid():
        Participant.update_row(session_id=session_id,
                               survey=my_survey,
                               form_name=form_name,
                               form_data=form.cleaned_data)
        return HttpResponse('success')
    else:
        return render(request, template_name='livesurvey/partials/partial_singleform.html')

    # needs to return htmx partial
    return HttpResponse('hi')

