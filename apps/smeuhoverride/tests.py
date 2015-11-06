# -*- encoding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth.models import User


class BaseTestCase(TestCase):

    def setUp(self):
        self.me = self.create_user('bob')
        self.login(self.me.username)
        self.her = self.create_user('alice')

    def create_user(self, username='bob'):
        return User.objects.create_user(username, password='secret')

    def login(self, username):
        self.client.login(username=username, password='secret')


class BaseImageTest(BaseTestCase):
    from os.path import join, dirname
    testfile = join(dirname(dirname(dirname(__file__))), 'tests', '1px.gif')


class TestHomePage(BaseTestCase):

    def test_home_page(self):
        resp = self.client.get('/')
        self.assertContains(resp, 'Homepage')
