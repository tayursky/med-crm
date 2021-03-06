# Generated by Django 2.2.1 on 2019-06-16 14:17

import absolutum.mixins.mixins
from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('identity', '0001_initial'),
        ('directory', '0001_initial'),
        ('company', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
            ],
            options={
                'proxy': True,
                'default_permissions': (),
                'verbose_name_plural': 'Пользователи',
                'constraints': [],
                'permissions': [('add_user', 'Добавлять пользователей'), ('change_user', 'Редактировать пользователей'), ('delete_user', 'Удалять пользователей'), ('view_user', 'Просматривать пользователей')],
                'indexes': [],
                'verbose_name': 'Пользователь',
            },
            bases=('identity.person',),
        ),
        migrations.CreateModel(
            name='UserGroup',
            fields=[
            ],
            options={
                'proxy': True,
                'ordering': ['name'],
                'verbose_name_plural': 'Группы доступа',
                'constraints': [],
                'permissions': [('add_usergroup', 'Добавлять группы доступа'), ('change_usergroup', 'Редактировать группы доступа'), ('delete_usergroup', 'Удалять группы доступа'), ('view_usergroup', 'Просматривать группы доступа')],
                'default_permissions': (),
                'indexes': [],
                'verbose_name': 'Группа доступа',
            },
            bases=('auth.group', absolutum.mixins.mixins.CoreMixin, absolutum.mixins.mixins.DisplayMixin),
            managers=[
                ('objects', django.contrib.auth.models.GroupManager()),
            ],
        ),
        migrations.AddField(
            model_name='historicalbranch',
            name='city',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='directory.City', verbose_name='Город'),
        ),
        migrations.AddField(
            model_name='historicalbranch',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='branch',
            name='city',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='directory.City', verbose_name='Город'),
        ),
    ]
