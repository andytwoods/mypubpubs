import random
import string

from django.test import TestCase

from livesurvey.factories import SurveyFactory
from livesurvey.models import Participant, Survey


def gen_session_id():
    return random.choices(string.ascii_letters + string.digits, k=32)



class ParticipantFactory(TestCase):
    def test_add_data__new(self):
        s: Survey = SurveyFactory()

        session_id = gen_session_id()
        post_data = {'a': 1}

        Participant.update_row(session_id=session_id, survey=s, post_data=post_data)

        found: Participant = Participant.objects.get(session_id=session_id)
        self.assertIsNotNone(found)

        self.assertEquals(found.data['a'], post_data['a'])


        Participant.update_row(session_id=session_id, survey=s, post_data={'b': 2})
        found.refresh_from_db()

        self.assertEquals(found.data['a'], post_data['a'])
        self.assertEquals(found.data['b'], 2)

