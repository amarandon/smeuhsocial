from django.core import mail
from smeuhoverride.tests import BaseTestCase
from smtplib import SMTPRecipientsRefused
from mock import patch


class TestTouites(BaseTestCase):

    def check_toggle_follow(self, action):

        self.login(self.me.username)

        resp = self.client.post(
            '/touites/toggle_follow/%s/' % self.her.username, {
                'action': action,
            }, follow=True)

        self.assertEqual(resp.status_code, 200)

    def test_follow(self):
        self.check_toggle_follow('follow')

    def test_unfollow(self):
        self.check_toggle_follow('unfollow')

    def test_post(self):
        response = self.client.post("/touites/post/", {
            'text': 'Touite Content'
        }, follow=True)
        self.assertContains(response, 'Touite Content')

    def test_get_list_no_param(self):
        response = self.client.get("/touites/")
        self.assertNotContains(response, "None")

    def test_get_list_with_reply_param(self):
        response = self.client.get("/touites/?reply=alice")
        self.assertContains(response, "@alice")

    def test_reply_send_notification_email(self):
        self.her.email = "alice@example.com"
        self.her.save()
        self.client.post("/touites/post/", {
            'text': '@alice Hi Alice!'
        }, follow=True)
        self.assertEqual(len(mail.outbox), 1)

    # When running the test suite the email backend is locmem
    @patch('django.core.mail.backends.locmem.EmailBackend')
    def test_reply_to_user_with_invalid_email_address(self, email_mock):
        # Simulate an SMTPRecipientsRefused exception
        email_mock.return_value.send_messages.side_effect = [
            SMTPRecipientsRefused('alice@example.com'),
            True,
        ]
        self.her.email = "alice@example.com"
        self.her.save()
        response = self.client.post("/touites/post/", {
            'text': '@alice Hi Alice!'
        }, follow=True)
        self.assertContains(response, 'Hi Alice')
        self.assertEqual(len(mail.outbox), 0)
