# Generated by Django 2.2.1 on 2020-02-11 14:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0044_auto_20200211_1458'),
    ]

    operations = [
        migrations.RenameField(
            model_name='branch',
            old_name='time',
            new_name='interval',
        ),
        migrations.RenameField(
            model_name='historicalbranch',
            old_name='time',
            new_name='interval',
        ),
    ]
