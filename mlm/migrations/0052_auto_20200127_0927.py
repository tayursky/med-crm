# Generated by Django 2.2.1 on 2020-01-27 09:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mlm', '0051_auto_20200125_0937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='parent',
            field=models.ForeignKey(blank=True, limit_choices_to={'position': 'manager'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_agents', to='mlm.Agent', verbose_name='Руководитель'),
        ),
        migrations.AlterField(
            model_name='historicalagent',
            name='parent',
            field=models.ForeignKey(blank=True, db_constraint=False, limit_choices_to={'position': 'manager'}, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='mlm.Agent', verbose_name='Руководитель'),
        ),
    ]