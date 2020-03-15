# Generated by Django 2.2.1 on 2019-10-28 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0012_auto_20191025_1037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicaltimetable',
            name='comment',
            field=models.TextField(blank=True, default='', verbose_name='Комментарий'),
        ),
        migrations.AlterField(
            model_name='historicaltimetable',
            name='fact_end_datetime',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Фактическое окончание смены'),
        ),
        migrations.AlterField(
            model_name='historicaltimetable',
            name='fact_start_datetime',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Фактическое начало смены'),
        ),
        migrations.AlterField(
            model_name='historicaltimetable',
            name='plan_end_datetime',
            field=models.DateTimeField(verbose_name='Плановое окончание смены'),
        ),
        migrations.AlterField(
            model_name='historicaltimetable',
            name='plan_start_datetime',
            field=models.DateTimeField(verbose_name='Плановое начало смены'),
        ),
        migrations.AlterField(
            model_name='timetable',
            name='comment',
            field=models.TextField(blank=True, default='', verbose_name='Комментарий'),
        ),
        migrations.AlterField(
            model_name='timetable',
            name='fact_end_datetime',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Фактическое окончание смены'),
        ),
        migrations.AlterField(
            model_name='timetable',
            name='fact_start_datetime',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Фактическое начало смены'),
        ),
        migrations.AlterField(
            model_name='timetable',
            name='plan_end_datetime',
            field=models.DateTimeField(verbose_name='Плановое окончание смены'),
        ),
        migrations.AlterField(
            model_name='timetable',
            name='plan_start_datetime',
            field=models.DateTimeField(verbose_name='Плановое начало смены'),
        ),
    ]