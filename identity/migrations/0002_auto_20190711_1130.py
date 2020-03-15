# Generated by Django 2.2.1 on 2019-07-11 11:30

import absolutum.mixins.mixins
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('identity', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='personemail',
            options={'default_permissions': (), 'ordering': ['value'], 'verbose_name': 'E-mail', 'verbose_name_plural': 'E-mail'},
        ),
        migrations.AlterModelOptions(
            name='personphone',
            options={'default_permissions': (), 'ordering': ['type', 'value'], 'verbose_name': 'Телефон', 'verbose_name_plural': 'Телефоны'},
        ),
        migrations.AlterField(
            model_name='historicalperson',
            name='timezone',
            field=models.SmallIntegerField(blank=True, help_text='Если часовой пояс отличен от города сделки', null=True, verbose_name='Часовой пояс'),
        ),
        migrations.AlterField(
            model_name='person',
            name='timezone',
            field=models.SmallIntegerField(blank=True, help_text='Если часовой пояс отличен от города сделки', null=True, verbose_name='Часовой пояс'),
        ),
        migrations.CreateModel(
            name='PersonContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.PositiveSmallIntegerField(choices=[(1, 'соц.сеть'), (2, 'мессенджер')], default=1, verbose_name='Тип контакта')),
                ('value', models.CharField(max_length=32, verbose_name='Доп. контакт')),
                ('comment', models.CharField(blank=True, max_length=124, null=True, verbose_name='Комментарий')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to='identity.Person', verbose_name='Персона')),
            ],
            options={
                'ordering': ['type', 'value'],
                'verbose_name': 'Доп. контакт',
                'verbose_name_plural': 'Доп. контакты',
                'default_permissions': (),
            },
            bases=(models.Model, absolutum.mixins.mixins.CoreMixin, absolutum.mixins.mixins.DisplayMixin),
        ),
    ]