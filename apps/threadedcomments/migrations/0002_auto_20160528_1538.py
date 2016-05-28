# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('threadedcomments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='threadedcomment',
            name='ip_address',
            field=models.GenericIPAddressField(null=True, verbose_name='IP address', blank=True),
        ),
    ]
