# Generated by Django 2.2.1 on 2020-03-04 17:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0050_auto_20200226_0949'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'default_permissions': (), 'permissions': [('add_user', 'Добавлять пользователей'), ('change_user', 'Редактировать пользователей'), ('delete_user', 'Удалять пользователей'), ('view_user', 'Просматривать пользователей'), ('reward_user', 'Просматривать вознаграждения сотрудников')], 'verbose_name': 'Сотрудник', 'verbose_name_plural': 'Сотрудники'},
        ),
    ]
