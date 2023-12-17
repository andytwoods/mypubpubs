import random
import string

import numpy
from django.test import TestCase

from livesurvey.factories import SurveyFactory, ParticipantFormDataFactory
from livesurvey.models import ParticipantFormData
from livesurvey.tools import gen_bounds, histogram_data, extract_dv, histogram_labels


def gen_session_id():
    return random.choices(string.ascii_letters + string.digits, k=32)


class TestParticipantFormData(TestCase):
    def test_chart_data(self):
        survey = SurveyFactory()
        form_name = 'my_form'
        form_field = 'bla'
        data = [1,2,1,2]
        for val in data:
            data = {form_field: val}
            p = ParticipantFormDataFactory(survey=survey,
                                       data=data,
                                       form=form_name)

        chart_data = ParticipantFormData.chart_data(survey=survey, form_name=form_name)
        self.assertCountEqual(chart_data, [{'bla': 1}, {'bla': 2}, {'bla': 1}, {'bla': 2}])

    def test_extract_dv(self):
        outcome = extract_dv([{'bla': 1}, {'bla': 2}, {'bla': 1}, {'bla': 2}], 'bla')
        self.assertEquals(outcome, [1,2,1,2])

        # no exception if missing key
        outcome = extract_dv([{'bla': 1}, {'not_here': 2}, {'bla': 1}, {'bla': 2}], 'bla')
        self.assertEquals(outcome, [1,1,2])

    def test_histogram_labels(self):
        outcome = histogram_labels([1,3,5,7])
        self.assertEquals(outcome, ['1 - 3', '3 - 5', '5 - 7'])


class TestGenBounds(TestCase):
    def test_gen_bounds(self):
        data = [1,2,3,4,5,5,5,6,7,8]
        outcome = histogram_data(data)
        print(outcome)