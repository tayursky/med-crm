# Generated by Django 2.2.1 on 2019-06-28 02:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deal', '0005_auto_20190626_0949'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalservicetemplate',
            name='periodic',
            field=models.BooleanField(default=False, verbose_name='Периодический'),
        ),
        migrations.AddField(
            model_name='servicetemplate',
            name='periodic',
            field=models.BooleanField(default=False, verbose_name='Периодический'),
        ),
    ]