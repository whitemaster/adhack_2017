# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-08-27 08:32
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0007_complitedtask'),
    ]

    operations = [
        migrations.AddField(
            model_name='extuser',
            name='key',
            field=models.CharField(blank=True, max_length=150, verbose_name='\u041a\u043b\u044e\u0447 \u0432 \u042d\u0444\u0438\u0440\u0435'),
        ),
        migrations.AlterField(
            model_name='complitedtask',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='complited', to='exchange.Task'),
        ),
        migrations.AlterField(
            model_name='complitedtask',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='complited', to=settings.AUTH_USER_MODEL),
        ),
    ]