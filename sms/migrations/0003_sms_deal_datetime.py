# Generated by Django 2.2.1 on 2019-07-10 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sms', '0002_auto_20190618_0921'),
    ]

    operations = [
        migrations.AddField(
            model_name='sms',
            name='deal_datetime',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Время сделки'),
        ),
    ]
