# -*- encoding: utf-8 -*-
from smeuhoverride.tests import BaseTestCase
from django.contrib.auth.models import User
from django.contrib import auth


class TestResetPassword(BaseTestCase):

    def test_post(self):
        from emailconfirmation.models import EmailAddress
        user = User.objects.create_user('foo', password='secret',
                                        email='foo@example.com')
        EmailAddress.objects.create(user=user, email=user.email, verified=True)
        response = self.client.post('/account/password_reset/',
                                    {'email': user.email}, follow=True)
        self.assertContains(response, u"Nous vous avons envoyé un email")


class TestSignup(BaseTestCase):

    def test_no_email(self):
        response = self.client.post(
            '/account/signup/', {
                'username': 'foo',
                'password1': 'bar',
                'password2': 'bar',
            }, follow=True)
        user = auth.get_user(self.client)
        self.assertContains(
            response, "Connecté en temps que foo avec succès.")
        self.assertTrue(user.is_authenticated())
