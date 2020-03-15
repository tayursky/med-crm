# Generated by Django 2.2.1 on 2019-07-30 12:23

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('identity', '0007_auto_20190711_1407'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalperson',
            name='cache',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='person',
            name='cache',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
    ]
