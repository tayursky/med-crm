# Generated by Django 2.2.1 on 2020-01-06 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mlm', '0027_auto_20191221_0936'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='contract_offer',
            field=models.BooleanField(default=False, verbose_name='Договор оферты'),
        ),
        migrations.AddField(
            model_name='historicalagent',
            name='contract_offer',
            field=models.BooleanField(default=False, verbose_name='Договор оферты'),
        ),
    ]
