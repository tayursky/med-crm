# Generated by Django 2.2.1 on 2019-07-23 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deal', '0015_auto_20190723_1219'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='day',
            field=models.DateField(verbose_name='День'),
        ),
        migrations.AlterField(
            model_name='expense',
            name='value',
            field=models.DecimalField(decimal_places=2, default='0.00', max_digits=30, verbose_name='Сумма'),
        ),
        migrations.AlterField(
            model_name='historicalexpense',
            name='day',
            field=models.DateField(default=None, verbose_name='День'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='historicalexpense',
            name='value',
            field=models.DecimalField(decimal_places=2, default='0.00', max_digits=30, verbose_name='Сумма'),
        ),
    ]
