# Generated by Django 2.2.1 on 2019-10-11 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('identity', '0015_auto_20190927_0830'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalperson',
            name='sip_id',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='SIP идентификатор'),
        ),
        migrations.AddField(
            model_name='person',
            name='sip_id',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='SIP идентификатор'),
        ),
    ]
