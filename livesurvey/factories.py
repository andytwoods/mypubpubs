import datetime
import random

import factory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyDateTime, FuzzyInteger, FuzzyText

from livesurvey.models import Participant, Survey


class ParticipantFactory(DjangoModelFactory):
    session_id = FuzzyText(length=32)

    class Meta:
        model = Participant


class SurveyFactory(DjangoModelFactory):
    title = FuzzyText(length=10)
    slug = FuzzyText(length=10)

    class Meta:
        model = Survey
