# Generated by Django 2.2.1 on 2019-06-28 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deal', '0006_auto_20190628_0227'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalservicetimetable',
            name='address',
            field=models.TextField(blank=True, null=True, verbose_name='Адрес'),
        ),
        migrations.AddField(
            model_name='servicetimetable',
            name='address',
            field=models.TextField(blank=True, null=True, verbose_name='Адрес'),
        ),
    ]