from datetime import timedelta

from django.test import TestCase, Client
from django.urls import reverse
from django.utils.timezone import now

from graffiti.models import GraffitiImage, Headset
from graffiti.tasks import every_five_mins, _every_five_mins
from graffiti.views import NO_IMAGE_RESPONSE


# Create your tests here.

class TasksTest(TestCase):
    def test_every_five_mins(self):
        headset = Headset(vr_id='my_id')
        headset.save()
        image = GraffitiImage(headset=headset)
        image.save()

        self.assertEquals(GraffitiImage.objects.count(), 1)
        _every_five_mins(now())
        self.assertEquals(GraffitiImage.objects.count(), 1)

        _every_five_mins(now() - timedelta(minutes=4, seconds=59))
        self.assertEquals(GraffitiImage.objects.count(), 1)

        _every_five_mins(now() - timedelta(minutes=5, seconds=1))
        self.assertEquals(GraffitiImage.objects.count(), 0)

class TextModels(TestCase):
    def test_check_valid(self):
        headset = Headset(vr_id='my_id')
        headset.save()
        image = GraffitiImage(headset=headset)
        image.save()

        self.assertIsNotNone(GraffitiImage.check_valid(image, now()))
        self.assertIsNotNone(GraffitiImage.check_valid(image, now() - timedelta(minutes=4, seconds=59)))
        self.assertIsNotNone(GraffitiImage.check_valid(image, now() - timedelta(minutes=5, seconds=1)))

class HeadsetProcessTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    def test_link_headset(self):

        self.assertEqual(Headset.objects.count(), 0)

        headset_id = 'headset_id'
        url = reverse('graffiti_code', kwargs={'vr_id': headset_id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        headset:Headset = Headset.objects.last()
        self.assertEquals(headset.vr_id, headset_id)

        json = response.json()

        code = json.get('code')
        url = json.get('url')

        self.assertTrue(code in url)
        self.assertEquals(headset.temp_code, code)

    def test_use_unknown_link_get_image(self):
        headset_id = 'headset_id'
        url = reverse('graffiti_image', kwargs={'vr_id': headset_id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_use_known_link_get_image_no_image(self):
        headset = Headset(vr_id='headset_id')
        headset.save()

        url = reverse('graffiti_image', kwargs={'vr_id': headset.vr_id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content.decode('utf-8'), NO_IMAGE_RESPONSE)

    def test_use_known_link_get_image_url(self):
        headset = Headset(vr_id='headset_id', )
        headset.save()

        image_url = 'https://example.com/image.jpg'
        image = GraffitiImage(headset=headset, url=image_url)
        image.save()

        url = reverse('graffiti_image', kwargs={'vr_id': headset.vr_id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content.decode('utf-8'), image_url)

    def test_multiple_headsets(self):
        client = Client()

        image_url = 'https://example.com/image.jpg'

        for my_id in range(5):
            my_headset = Headset(vr_id=f'headset_{my_id}', )
            my_headset.save()
            if my_id % 2 == 0:
                my_image = GraffitiImage(headset=my_headset, url=image_url + str(my_id))
                my_image.save()

        headset = Headset(vr_id='headset_id', )
        headset.save()

        for my_id in range(5, 10):
            my_headset = Headset(vr_id=f'headset_{my_id}', )
            my_headset.save()
            if my_id % 2 == 0:
                my_image = GraffitiImage(headset=my_headset, url=image_url + str(my_id))
                my_image.save()

        image_url = 'https://example.com/image.jpg'
        image = GraffitiImage(headset=headset, url=image_url)
        image.save()

        url = reverse('graffiti_image', kwargs={'vr_id': headset.vr_id})
        response = client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content.decode('utf-8'), image_url)

class AddImageForm(TestCase):
    def test_add_image_url(self):
        headset = Headset(vr_id='headset_id')
        headset.save()

        image_url = 'https://example.com/image.jpg'

        url = reverse('graffiti_linkup', kwargs={'temp_code': headset.temp_code})
        response = self.client.post(url, {
            'url': image_url,
        })
        self.assertEquals(response.status_code, 200)

        image = GraffitiImage.objects.filter(headset=headset).first()
        self.assertEqual(image.url, image_url)

        # let's check that the returned image_url is as expected
        url = reverse('graffiti_image', kwargs={'vr_id': headset.vr_id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content.decode('utf-8'), image_url)

        # let's update the url and check that we get the expected new url
        image_url2 = 'https://example.com/image2.jpg'
        url = reverse('graffiti_linkup', kwargs={'temp_code': headset.temp_code})
        response = self.client.post(url, {
            'url': image_url2,
        })

        url = reverse('graffiti_image', kwargs={'vr_id': headset.vr_id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content.decode('utf-8'), image_url2)

