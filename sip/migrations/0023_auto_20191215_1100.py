# Generated by Django 2.2.1 on 2019-12-15 11:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sip', '0022_auto_20191215_1033'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='log',
            options={'default_permissions': (), 'ordering': ['-entry_datetime'], 'permissions': [('view_log', 'Просматривать журнал')], 'verbose_name': 'Запись в журнале телефонии', 'verbose_name_plural': 'Журнал телефонии'},
        ),
    ]
