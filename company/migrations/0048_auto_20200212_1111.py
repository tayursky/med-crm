# Generated by Django 2.2.1 on 2020-02-12 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0047_auto_20200212_0918'),
    ]

    operations = [
        migrations.AddField(
            model_name='branch',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Активный'),
        ),
        migrations.AddField(
            model_name='historicalbranch',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Активный'),
        ),
    ]
