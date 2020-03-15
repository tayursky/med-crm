# Generated by Django 2.2.1 on 2019-09-19 11:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('identity', '0013_auto_20190825_1203'),
        ('company', '0007_auto_20190901_1004'),
    ]

    operations = [
        migrations.CreateModel(
            name='Manager',
            fields=[
            ],
            options={
                'default_permissions': (),
                'constraints': [],
                'indexes': [],
                'permissions': [],
                'verbose_name': 'Организатор',
                'verbose_name_plural': 'Организаторы',
                'proxy': True,
            },
            bases=('identity.person',),
        ),
        migrations.CreateModel(
            name='Master',
            fields=[
            ],
            options={
                'default_permissions': (),
                'constraints': [],
                'indexes': [],
                'permissions': [],
                'verbose_name': 'Правщик',
                'verbose_name_plural': 'Правщики',
                'proxy': True,
            },
            bases=('identity.person',),
        ),
    ]