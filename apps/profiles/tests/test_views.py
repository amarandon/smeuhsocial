from smeuhoverride.tests import BaseTestCase


class TestEditProfile(BaseTestCase):

    def test_get_edit_profile(self):
        response = self.client.get("/profiles/edit/")
        self.assertContains(response, "bob")

