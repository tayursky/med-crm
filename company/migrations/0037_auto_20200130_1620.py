# Generated by Django 2.2.1 on 2020-01-30 16:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0036_merge_20200129_1545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timegroup',
            name='branch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='time_groups', to='company.Branch', verbose_name='Филиал'),
        ),
    ]
