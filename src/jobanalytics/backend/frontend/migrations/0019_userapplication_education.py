# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-04-29 22:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0018_userapplication_work_experience'),
    ]

    operations = [
        migrations.AddField(
            model_name='userapplication',
            name='education',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
