from smeuhoverride.tests import BaseImageTest
from avatar.models import Avatar


class TestAvatar(BaseImageTest):

    def upload_avatar(self):
        return self.client.post('/avatar/change/', {
            'avatar': open(self.testfile),
        }, follow=True)

    def test_upload_avatar(self):
        resp = self.upload_avatar()
        self.assertContains(resp, 'Successfully uploaded a new avatar')

    def test_change_avatar(self):
        self.upload_avatar()
        resp = self.client.post('/avatar/change/', {
            'choice': Avatar.objects.get().pk,
        }, follow=True)
        self.assertContains(resp, 'Successfully updated')

    def test_delete_avatar(self):
        self.upload_avatar()
        resp = self.client.post('/avatar/delete/', {
            'choices': [Avatar.objects.get().pk],
        }, follow=True)
        self.assertContains(resp, 'Successfully deleted')

