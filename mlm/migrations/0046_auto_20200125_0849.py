# Generated by Django 2.2.1 on 2020-01-25 08:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mlm', '0045_auto_20200125_0843'),
    ]

    operations = [
        migrations.RenameField(
            model_name='historicalagent',
            old_name='referral',
            new_name='referrer',
        ),
        migrations.RemoveField(
            model_name='agent',
            name='referral',
        ),
        migrations.AddField(
            model_name='agent',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_agents', to='mlm.Agent', verbose_name='Менеджер'),
        ),
        migrations.AddField(
            model_name='agent',
            name='referrer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invite_agents', to='mlm.Agent', verbose_name='Кто привел'),
        ),
        migrations.AddField(
            model_name='historicalagent',
            name='parent',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='mlm.Agent', verbose_name='Менеджер'),
        ),
    ]
