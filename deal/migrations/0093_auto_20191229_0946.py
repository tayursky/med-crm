# Generated by Django 2.2.1 on 2019-12-29 09:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deal', '0092_auto_20191229_0945'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='servicetimetable',
            options={'default_permissions': (), 'ordering': ['start_datetime'], 'permissions': [('add_servicetimetable', 'Добавлять расписание для услуг'), ('change_servicetimetable', 'Редактировать расписание для услуг'), ('delete_servicetimetable', 'Удалять расписание для услуг'), ('view_servicetimetable', 'Просматривать расписание для услуг')], 'verbose_name': 'Услуга: расписание', 'verbose_name_plural': 'Услуги: расписание'},
        ),
    ]