# Generated by Django 2.2.1 on 2019-12-28 11:14

import absolutum.mixins.mixins
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('deal', '0076_auto_20191228_1043'),
    ]

    operations = [
        migrations.CreateModel(
            name='Stage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=32, null=True, verbose_name='Метка')),
                ('label', models.CharField(blank=True, max_length=32, null=True, verbose_name='Наименование')),
                ('step', models.IntegerField(default=0, verbose_name='Последовательность')),
                ('color', models.CharField(blank=True, default='#000000', max_length=7, verbose_name='Цвет текста')),
                ('background_color', models.CharField(blank=True, default='#ffffff', max_length=7, verbose_name='Цвет фона')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='Комментарий')),
            ],
            options={
                'default_permissions': (),
                'ordering': ['step'],
                'verbose_name': 'Этап сделки',
                'permissions': [('add_stage', 'Добавлять этапы сделки'), ('change_stage', 'Редактировать этапы сделки'), ('delete_stage', 'Удалять этапы сделки'), ('view_stage', 'Просматривать этапы сделки')],
                'verbose_name_plural': 'Этапы сделок',
            },
            bases=(models.Model, absolutum.mixins.mixins.CoreMixin, absolutum.mixins.mixins.DisplayMixin),
        ),
        migrations.AlterField(
            model_name='deal',
            name='manager',
            field=models.ForeignKey(blank=True, limit_choices_to={'account__groups__name__in': ['Организаторы']}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='manager_deals', to='company.Manager', verbose_name='Администратор'),
        ),
        migrations.AlterField(
            model_name='deal',
            name='master',
            field=models.ForeignKey(blank=True, limit_choices_to={'account__groups__name__in': ['Правщики']}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='master_deals', to='company.Master', verbose_name='Специалист'),
        ),
        migrations.AlterField(
            model_name='deal',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='deal.Service', verbose_name='Филиал (старая услуга)'),
        ),
        migrations.AlterField(
            model_name='deal',
            name='step',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='deal.ServiceTemplateStep', verbose_name='Этап (старый)'),
        ),
        migrations.AlterField(
            model_name='historicaldeal',
            name='manager',
            field=models.ForeignKey(blank=True, db_constraint=False, limit_choices_to={'account__groups__name__in': ['Организаторы']}, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='company.Manager', verbose_name='Администратор'),
        ),
        migrations.AlterField(
            model_name='historicaldeal',
            name='master',
            field=models.ForeignKey(blank=True, db_constraint=False, limit_choices_to={'account__groups__name__in': ['Правщики']}, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='company.Master', verbose_name='Специалист'),
        ),
        migrations.AlterField(
            model_name='historicaldeal',
            name='service',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='deal.Service', verbose_name='Филиал (старая услуга)'),
        ),
        migrations.AlterField(
            model_name='historicaldeal',
            name='step',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='deal.ServiceTemplateStep', verbose_name='Этап (старый)'),
        ),
        migrations.AddField(
            model_name='deal',
            name='stage',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='deal.Stage', verbose_name='Этап'),
        ),
        migrations.AddField(
            model_name='historicaldeal',
            name='stage',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='deal.Stage', verbose_name='Этап'),
        ),
    ]