# Generated by Django 2.2.1 on 2019-12-28 13:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deal', '0081_auto_20191228_1319'),
    ]

    operations = [
        migrations.RenameField(
            model_name='service',
            old_name='masters_n',
            new_name='masters',
        ),
    ]
