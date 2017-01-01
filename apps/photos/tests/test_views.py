# coding=utf-8
import os
from smeuhoverride.tests import BaseImageTest
from django.test import override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from photos.models import Image
from photos.tests.helpers import ImageTestMixin, DATA_DIR


class TestPhotos(ImageTestMixin, BaseImageTest):

    @override_settings(MEDIA_ROOT=DATA_DIR)
    def test_listing(self):
        self.create_image()
        response = self.client.get("/photos/")
        self.assertEqual(response.status_code, 200)

    @override_settings(MEDIA_ROOT=DATA_DIR)
    def test_details(self):
        image = self.create_image()
        response = self.client.get("/photos/details/%s/" % image.pk)
        self.assertEqual(response.status_code, 200)

    @override_settings(MEDIA_ROOT=DATA_DIR)
    def test_detail(self):
        user = User.objects.create_user(
            'testuser',
            'testuser@gmail.com',
            'password',
        )
        self.create_image()
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
