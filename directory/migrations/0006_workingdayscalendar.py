# Generated by Django 2.2.1 on 2019-11-30 13:57

import absolutum.mixins.mixins
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0005_auto_20191130_1341'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkingDaysCalendar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.DateField(null=True)),
                ('day_type', models.CharField(choices=[('workday', 'Рабочий день'), ('weekend', 'Выходной'), ('pre_holiday', 'Предпраздничный день'), ('holiday', 'Праздник')], default='workday', max_length=32, verbose_name='Статус сделки')),
                ('description', models.TextField(default='')),
            ],
            options={
                'permissions': [('add_workingdayscalendar', 'Добавлять производственный календарь'), ('view_workingdayscalendar', 'Просматривать производственный календарь')],
                'verbose_name_plural': 'Производственный календарь',
                'verbose_name': 'Производственный календарь',
                'ordering': ['day'],
                'default_permissions': (),
            },
            bases=(models.Model, absolutum.mixins.mixins.CoreMixin, absolutum.mixins.mixins.DisplayMixin),
        ),
    ]
