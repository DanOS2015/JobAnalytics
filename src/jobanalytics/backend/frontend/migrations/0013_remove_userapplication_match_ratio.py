# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-04-20 13:02
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0012_auto_20180420_1348'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userapplication',
            name='match_ratio',
        ),
    ]
