# Generated by Django 2.2.1 on 2019-12-12 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sip', '0012_mightycalluser_extension_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mightycalluser',
            name='user_key',
            field=models.CharField(help_text='Сгенерированный ключ пользователя', max_length=256, verbose_name='Ключ пользователя'),
        ),
    ]
