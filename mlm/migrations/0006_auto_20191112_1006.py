# Generated by Django 2.2.1 on 2019-11-12 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mlm', '0005_auto_20191111_1150'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='discount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5, verbose_name='Скидка'),
        ),
        migrations.AddField(
            model_name='historicalagent',
            name='discount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5, verbose_name='Скидка'),
        ),
    ]
