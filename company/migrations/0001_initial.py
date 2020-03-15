# Generated by Django 2.2.1 on 2019-06-16 14:17

import absolutum.mixins.mixins
from django.db import migrations, models
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='Наименование')),
            ],
            options={
                'ordering': ['city', 'name'],
                'verbose_name_plural': 'Филиалы',
                'permissions': [('add_branch', 'Добавлять филиалы'), ('change_branch', 'Редактировать филиалы'), ('delete_branch', 'Удалять филиалы'), ('view_branch', 'Просматривать филиалы')],
                'default_permissions': (),
                'verbose_name': 'Филиал',
            },
            bases=(models.Model, absolutum.mixins.mixins.CoreMixin, absolutum.mixins.mixins.DisplayMixin),
        ),
        migrations.CreateModel(
            name='HistoricalBranch',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='Наименование')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical Филиал',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]