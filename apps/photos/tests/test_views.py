# coding=utf-8
import os
import shutil
from smeuhoverride.tests import BaseImageTest
from django.test import override_settings
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from photos.models import Image


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class TestPhotos(BaseImageTest):

    filepath = os.path.join(DATA_DIR, u"Là où j ai dormi cette nuit.jpg")

    def tearDown(self):
        filename = os.path.join(DATA_DIR, "La_ou_j_ai_dormi_cette_nuit.jpg")
        if os.path.exists(filename):
            os.unlink(filename)
        cache_dir = os.path.join(DATA_DIR, "cache")
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)

    @override_settings(MEDIA_ROOT=DATA_DIR)
    def test_listing(self):
        Image.objects.create(member=self.me, title="test photo",
                             image=File(open(self.filepath)))
        response = self.client.get("/photos/")
        self.assertEqual(response.status_code, 200)

    @override_settings(MEDIA_ROOT=DATA_DIR)
    def test_details(self):
        image = Image.objects.create(member=self.me, title="test photo",
                                     image=File(open(self.filepath)))
        response = self.client.get("/photos/details/%s/" % image.pk)
        self.assertEqual(response.status_code, 200)

    @override_settings(MEDIA_ROOT=DATA_DIR)
    def test_detail(self):
        user = User.objects.create_user(
            'testuser',
            'testuser@gmail.com',
            'password',
        )
        Image.objects.create(member=user, title="test photo",
                             image=File(open(self.filepath)))
        response = self.client.get("/photos/")
        self.assertEqual(response.status_code, 200)

    def test_upload_from_contains_css_url(self):
        response = self.client.get("/photos/upload/")
        self.assertContains(response, "/media/static/pinax/css/base.css")

    def test_upload(self):
        image_count = Image.objects.count()
        content = open(self.filepath, "rb")
        response = self.client.post("/photos/upload/", {
            "title": "Test photo",
            "image": SimpleUploadedFile("test.jpg", content.read(),
                                        "image/jpeg"),
            "action": "upload",
            "safetylevel": 1,
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Image.objects.count(), image_count + 1)
