# Generated by Django 2.2.1 on 2019-12-08 11:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sip', '0006_mightycalluser'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mightycalluser',
            options={'default_permissions': (), 'ordering': ['name'], 'permissions': [('add_mightycalluser', 'Добавлять пользователей яндекс.телефонии'), ('change_mightycalluser', 'Редактировать пользователей яндекс.телефонии'), ('delete_mightycalluser', 'Удалять пользователей яндекс.телефонии'), ('view_mightycalluser', 'Просматривать пользователей яндекс.телефонии')], 'verbose_name': 'Пользователь яндекс.телефонии', 'verbose_name_plural': 'Пользователи яндекс.телефонии'},
        ),
    ]
