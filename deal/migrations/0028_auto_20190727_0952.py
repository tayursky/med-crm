# Generated by Django 2.2.1 on 2019-07-27 09:52

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deal', '0027_auto_20190727_0951'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deal',
            name='cache',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='historicaldeal',
            name='cache',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
    ]
