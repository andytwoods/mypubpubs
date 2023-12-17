import json
import uuid

from django.http import HttpResponse
from django.shortcuts import render

from livesurvey.models import Survey, ParticipantFormData
from .forms import DemographicsForm, Histogram, Pie

from livesurvey.tools import gen_bounds, histogram_data, extract_dv, pie_data
from .tools import get_livesurvey_forms, get_livesurvey_form, gen_bounds
import numpy


# Create your views here.

def survey(request, survey_slug):
    # my_survey: Survey = Survey.objects.get(slug=survey_slug)
    forms = get_livesurvey_forms()

    return render(request, 'livesurvey/livesurvey.html', context={'forms': forms})


def get_session_id(request):
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key


def graph_post(request, survey: Survey, form_name: str):
    form = get_livesurvey_form(form_name)
    unique_id = uuid.uuid4()

    context = {}
    data = ParticipantFormData.chart_data(survey=survey, form_name=form_name)
    data_list = extract_dv(data, form.dv)

    template = ''

    if issubclass(form, Histogram):
        data_all, labels = histogram_data(data_list)
        context.update({'data': {'vals': data_all, 'labels': labels}, 'unique_id': unique_id})
        template = 'livesurvey/partials/partial_histogram.html'
    elif issubclass(form, Pie):
        dv_element = form.base_fields[form.dv]
        choices = dv_element.choices
        data_all, labels = pie_data(data_list, choices)
        context.update({'data': {'vals': data_all, 'labels': labels}, 'unique_id': unique_id})
        template = 'livesurvey/partials/partial_pie.html'
    return render(request, template, context=context)


def survey_post(request, survey_slug, form_name):
    # below should never be None as POST (and first generated on GET)
    my_survey: Survey
    try:
        my_survey = Survey.objects.get(slug=survey_slug)
    except Survey.DoesNotExist:

        my_survey = Survey(slug=survey_slug, title='local host demo survey autocreated')
        my_survey.save()

    session_id = get_session_id(request)
    form_data = request.POST

    form_cls = get_livesurvey_form(form_name)

    form = form_cls(data=form_data)
    if form.is_valid():
        ParticipantFormData.update_row(session_id=session_id,
                                       survey=my_survey,
                                       form_name=form_name,
                                       form_data=form.cleaned_data)
        return graph_post(request, my_survey, form_name)
    else:
        return render(request, template_name='livesurvey/partials/partial_singleform.html')

    # needs to return htmx partial
