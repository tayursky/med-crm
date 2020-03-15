# Generated by Django 2.2.1 on 2020-01-23 10:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mlm', '0042_auto_20200122_1317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_agents', to='mlm.Agent', verbose_name='Кто привел'),
        ),
    ]
