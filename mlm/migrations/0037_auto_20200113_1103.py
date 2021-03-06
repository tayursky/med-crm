# Generated by Django 2.2.1 on 2020-01-13 11:03

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mlm', '0036_auto_20200113_1042'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Время создания'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalagent',
            name='created_at',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False, verbose_name='Время создания'),
            preserve_default=False,
        ),
    ]
