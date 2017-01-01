from smeuhoverride.tests import BaseTestCase
from django.test import override_settings
from photos.tests.helpers import ImageTestMixin, DATA_DIR


class TestViews(ImageTestMixin, BaseTestCase):

    @override_settings(MEDIA_ROOT=DATA_DIR)
    def test_get_index(self):
        self.create_image()
        response = self.client.get('/fu/', follow=True)
        self.assertEqual(response.status_code, 200)
