# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-08-26 17:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='extuser',
            name='balans',
            field=models.FloatField(default=0, verbose_name='\u0411\u0430\u043b\u0430\u043d\u0441'),
        ),
    ]
