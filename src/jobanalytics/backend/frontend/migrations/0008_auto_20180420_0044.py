# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-04-19 23:44
from __future__ import unicode_literals

import django.core.files.storage
import django.core.validators
from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0007_applicant'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicant',
            name='curriculum_vitae',
            field=models.FileField(default='', storage=django.core.files.storage.FileSystemStorage(location='C:\\Users\\dan36\\Desktop\\2018-ca400-osulld42\\src\\jobanalytics\\backend\\media\\cvs'), upload_to='', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['docx'])]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='applicant',
            name='email',
            field=models.EmailField(default='', max_length=70),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='applicant',
            name='last_name',
            field=models.CharField(default='', max_length=40),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='applicant',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(default='', max_length=128),
            preserve_default=False,
        ),
    ]
