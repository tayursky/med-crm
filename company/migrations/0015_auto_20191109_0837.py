# Generated by Django 2.2.1 on 2019-11-09 08:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0014_auto_20191105_1152'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'default_permissions': (), 'permissions': [('add_user', 'Добавлять пользователей'), ('change_user', 'Редактировать пользователей'), ('delete_user', 'Удалять пользователей'), ('view_user', 'Просматривать пользователей')], 'verbose_name': 'Сотрудник', 'verbose_name_plural': 'Сотрудники'},
        ),
    ]