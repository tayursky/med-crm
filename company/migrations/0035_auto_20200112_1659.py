# Generated by Django 2.2.1 on 2020-01-12 16:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0034_auto_20200112_1604'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timegroup',
            name='branch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timegroups', to='company.Branch', verbose_name='Филиал'),
        ),
    ]
