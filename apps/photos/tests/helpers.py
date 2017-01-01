# coding=utf-8
import shutil
import os
from photos.models import Image
from django.core.files import File


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class ImageTestMixin(object):

    filepath = os.path.join(DATA_DIR, u"Là où j ai dormi cette nuit.jpg")

    def tearDown(self):
        filename = os.path.join(DATA_DIR, "La_ou_j_ai_dormi_cette_nuit.jpg")
        if os.path.exists(filename):
            os.unlink(filename)
        cache_dir = os.path.join(DATA_DIR, "cache")
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)

    def create_image(self):
        django_file = File(open(self.filepath))
        image = Image.objects.create(member=self.me, title="test photo",
                                     image=django_file)
        return image
