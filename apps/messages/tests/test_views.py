from apps.smeuhoverride.tests import BaseTestCase
from messages.models import Message


class TestMessages(BaseTestCase):

    def create_message(self):
        message = Message(sender=self.her, recipient=self.me,
                          subject='Subject Text', body='Body Text')
        message.save()
        return message

    def test_reply(self):
        message = self.create_message()
        self.client.post('/messages/reply/%s/' % message.pk, {
            'body': 'Reply body',
            'recipient': message.sender.username,
            'subject': 'Re: Subject Text',
        })

    def test_delete(self):
        message = self.create_message()
        self.client.post('/messages/delete/%s/' % message.pk, {
            'body': 'Reply body',
            'recipient': message.sender.username,
            'subject': 'Re: Subject Text',
        })

    def test_compose(self):
        self.client.post('/messages/compose/', {
            'body': 'Message body',
            'recipient': self.her.username,
            'subject': 'Subject text',
        })
