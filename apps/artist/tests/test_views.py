from smeuhoverride.tests import BaseTestCase


class TestTimeline(BaseTestCase):

    def test_get_artist_index(self):
        response = self.client.get('/artist/')
        self.assertEqual(response.status_code, 200)

    def test_get_artist_details(self):
        response = self.client.get('/artist/bob/')
        self.assertEqual(response.status_code, 200)
