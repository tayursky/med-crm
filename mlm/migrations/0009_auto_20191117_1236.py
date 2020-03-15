# Generated by Django 2.2.1 on 2019-11-17 12:36

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mlm', '0008_auto_20191116_1425'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='code',
            field=models.CharField(max_length=32, unique=True, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z]*$', 'Только латинские буквы и цифры')], verbose_name='Промокод'),
        ),
        migrations.AlterField(
            model_name='historicalagent',
            name='code',
            field=models.CharField(db_index=True, max_length=32, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z]*$', 'Только латинские буквы и цифры')], verbose_name='Промокод'),
        ),
    ]
