# Generated by Django 2.2.1 on 2019-10-22 09:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sms', '0010_apitest'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='apitest',
            options={'default_permissions': (), 'ordering': ['-created_at'], 'permissions': [], 'verbose_name': 'Тест', 'verbose_name_plural': 'Тест'},
        ),
        migrations.RenameField(
            model_name='apitest',
            old_name='time_created',
            new_name='created_at',
        ),
    ]
