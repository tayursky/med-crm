# Generated by Django 2.2.1 on 2019-11-18 12:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mlm', '0012_auto_20191118_1213'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invite',
            name='paid_at',
        ),
        migrations.RemoveField(
            model_name='invite',
            name='paid_by',
        ),
    ]
