# Generated by Django 2.2.1 on 2019-11-19 08:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mlm', '0017_invite'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='invite',
            unique_together=set(),
        ),
    ]
