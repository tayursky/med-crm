# Generated by Django 2.2.1 on 2020-02-26 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0048_auto_20200212_1111'),
    ]

    operations = [
        migrations.AddField(
            model_name='branch',
            name='position',
            field=models.SmallIntegerField(blank=True, default=0, verbose_name='Сортировка'),
        ),
        migrations.AddField(
            model_name='historicalbranch',
            name='position',
            field=models.SmallIntegerField(blank=True, default=0, verbose_name='Сортировка'),
        ),
    ]
