# Generated by Django 2.2.1 on 2019-12-08 14:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sip', '0010_auto_20191208_1141'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mightycalluser',
            old_name='token_refresh',
            new_name='refresh_token',
        ),
    ]
