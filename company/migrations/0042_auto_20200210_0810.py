# Generated by Django 2.2.1 on 2020-02-10 08:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0041_timegroup_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='timegroup',
            old_name='user',
            new_name='users',
        ),
    ]