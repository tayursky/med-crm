# Generated by Django 2.2.1 on 2019-12-15 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sip', '0018_auto_20191215_1009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='event_type',
            field=models.CharField(max_length=128, verbose_name='Тип события'),
        ),
    ]
