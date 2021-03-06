# Generated by Django 2.2.1 on 2019-09-07 10:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('deal', '0044_auto_20190907_1025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='department',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='expenses', to='company.Department', verbose_name='Отделы'),
        ),
        migrations.AlterField(
            model_name='historicalexpense',
            name='department',
            field=models.ForeignKey(blank=True, db_constraint=False, default=1, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='company.Department', verbose_name='Отделы'),
        ),
    ]
