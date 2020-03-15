# Generated by Django 2.2.1 on 2019-12-28 10:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0020_auto_20191228_1036'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('deal', '0075_auto_20191228_1004'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groupservice',
            name='description',
        ),
        migrations.RemoveField(
            model_name='historicalservice',
            name='default_master',
        ),
        migrations.RemoveField(
            model_name='service',
            name='default_master',
        ),
        migrations.AddField(
            model_name='groupservice',
            name='comment',
            field=models.TextField(blank=True, null=True, verbose_name='Комментарий'),
        ),
    ]
