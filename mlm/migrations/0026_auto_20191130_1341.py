# Generated by Django 2.2.1 on 2019-11-30 13:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mlm', '0025_auto_20191120_0754'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='agent',
            options={'default_permissions': (), 'ordering': ['-cache__invite_balance', 'person'], 'permissions': [('add_agent', 'Добавлять агентов'), ('change_agent', 'Редактировать агентов'), ('delete_agent', 'Удалять агентов'), ('view_agent', 'Просматривать агентов')], 'verbose_name': 'Агент', 'verbose_name_plural': 'Агенты'},
        ),
    ]