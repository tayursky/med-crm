# Generated by Django 2.2.1 on 2020-01-23 11:40

import absolutum.mixins.mixins
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mlm', '0043_auto_20200123_1035'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgentTurnover',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('week', 'Недельный'), ('month', 'Месячный'), ('year', 'Годовой')], default='month', max_length=32, verbose_name='Период')),
                ('total', models.DecimalField(blank=True, decimal_places=2, default='0.00', max_digits=30, verbose_name='Оборот')),
                ('percent', models.DecimalField(blank=True, decimal_places=2, default='0.00', max_digits=10, verbose_name='Процент')),
                ('income', models.DecimalField(blank=True, decimal_places=2, default='0.00', max_digits=30, verbose_name='Доход')),
                ('date', models.DateField(verbose_name='Дата')),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='turnovers', to='mlm.Agent', verbose_name='Агент')),
            ],
            options={
                'verbose_name_plural': 'Обороты агентов',
                'verbose_name': 'Оборот агента',
                'permissions': [],
                'default_permissions': (),
            },
            bases=(models.Model, absolutum.mixins.mixins.CoreMixin, absolutum.mixins.mixins.DisplayMixin),
        ),
    ]
