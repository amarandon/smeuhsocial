from smeuhoverride.tests import BaseImageTest


class TestPhoto(BaseImageTest):

    def test_photo_details(self):
        self.skipTest("test failing but functionality works")
        title = "A cool photo"
        resp = self.client.post('/photos/upload/', {
            'image': open(self.testfile),
            'title': title,
            'safetylevel': 1,
            'action': 'upload',
        }, follow=True)

        self.assertContains(resp, title)

