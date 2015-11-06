from smeuhoverride.tests import BaseTestCase


class TestFriends(BaseTestCase):

    def test_invite(self):
        response = self.client.post('/%s/' % self.her.username, {
            'to_user': self.her.username,
            'action': u'invite',
            'message': u"Let's be friends!",
        }, follow=True)

        self.assertContains(
            response,
            "Friendship requested with %s" % self.her.username)


class TestInvite(BaseTestCase):

    def test_invite_new_user(self):
        resp = self.client.post('/invitations/invite/', {
            'email': 'somebody@example.com',
            'message': 'Message body',
        }, follow=True)

        self.assertContains(
            resp,
            'Invitation to join sent to somebody@example.com')
