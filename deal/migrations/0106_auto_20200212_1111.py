# Generated by Django 2.2.1 on 2020-02-12 11:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deal', '0105_auto_20200211_1529'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='report',
            options={'default_permissions': (), 'ordering': ['branch', 'start_datetime'], 'permissions': [], 'verbose_name': 'Отчет', 'verbose_name_plural': 'Отчеты'},
        ),
    ]
