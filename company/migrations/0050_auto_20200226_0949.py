# Generated by Django 2.2.1 on 2020-02-26 09:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0049_auto_20200226_0947'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='branch',
            options={'default_permissions': (), 'ordering': ['-position', 'city', 'name'], 'permissions': [('add_branch', 'Добавлять филиалы'), ('change_branch', 'Редактировать филиалы'), ('delete_branch', 'Удалять филиалы'), ('view_branch', 'Просматривать филиалы')], 'verbose_name': 'Филиал', 'verbose_name_plural': 'Филиалы'},
        ),
    ]
