from smeuhoverride.tests import BaseTestCase


class TestTimeline(BaseTestCase):

    def test_get_user_timeline(self):
        response = self.client.get('/timeline/user/bob/')
        self.assertEqual(response.status_code, 200)

    def test_get_following_timeline(self):
        self.client.login(username='bob', password='secret')
        response = self.client.get('/timeline/following')
        self.assertEqual(response.status_code, 200)

    def test_get_friends_timeline(self):
        self.client.login(username='bob', password='secret')
        response = self.client.get('/timeline/friends')
        self.assertEqual(response.status_code, 200)

