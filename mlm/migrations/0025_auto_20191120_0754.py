# Generated by Django 2.2.1 on 2019-11-20 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mlm', '0024_auto_20191119_1514'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='bank_account',
            field=models.TextField(blank=True, default='', verbose_name='Реквизиты'),
        ),
        migrations.AlterField(
            model_name='historicalagent',
            name='bank_account',
            field=models.TextField(blank=True, default='', verbose_name='Реквизиты'),
        ),
    ]
