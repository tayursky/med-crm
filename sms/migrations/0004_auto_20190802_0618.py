# Generated by Django 2.2.1 on 2019-08-02 06:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sms', '0003_sms_deal_datetime'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='smstemplate',
            options={'default_permissions': (), 'ordering': ['name'], 'permissions': [('add_smstemplate', 'Добавлять СМС: шаблон'), ('change_smstemplate', 'Редактировать СМС: шаблон'), ('delete_smstemplate', 'Удалять СМС: шаблон'), ('view_smstemplate', 'Просматривать СМС: шаблон')], 'verbose_name': 'СМС: шаблон', 'verbose_name_plural': 'СМС: шаблоны'},
        ),
    ]