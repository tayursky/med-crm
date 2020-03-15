# Generated by Django 2.2.1 on 2020-01-10 15:10

import absolutum.mixins.mixins
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('company', '0026_auto_20200106_0849'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timetable',
            name='branch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timetables', to='company.Branch', verbose_name='Филиал'),
        ),
        migrations.CreateModel(
            name='TimeGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=128, verbose_name='Наименование')),
                ('start_time', models.TimeField(blank=True, null=True, verbose_name='Начало интервала')),
                ('finish_time', models.TimeField(blank=True, null=True, verbose_name='Конец интервала')),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='time_groups', to='company.Branch', verbose_name='Филиал')),
            ],
            options={
                'verbose_name': 'Группа в расписании',
                'permissions': [('add_timegroup', 'Добавлять группы для расписания'), ('change_timegroup', 'Редактировать группы для расписания'), ('delete_timegroup', 'Удалять группы для расписания'), ('view_timegroup', 'Просматривать группы для расписания')],
                'ordering': ['branch', 'start_time'],
                'default_permissions': (),
                'verbose_name_plural': 'Группы для расписания',
            },
            bases=(models.Model, absolutum.mixins.mixins.CoreMixin, absolutum.mixins.mixins.DisplayMixin),
        ),
        migrations.CreateModel(
            name='HistoricalTimeGroup',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=128, verbose_name='Наименование')),
                ('start_time', models.TimeField(blank=True, null=True, verbose_name='Начало интервала')),
                ('finish_time', models.TimeField(blank=True, null=True, verbose_name='Конец интервала')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('branch', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='company.Branch', verbose_name='Филиал')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Группа в расписании',
                'get_latest_by': 'history_date',
                'ordering': ('-history_date', '-history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]