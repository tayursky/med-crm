# Generated by Django 2.2.1 on 2019-10-15 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sip', '0003_auto_20191015_0922'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='log',
            name='phone',
        ),
        migrations.RemoveField(
            model_name='log',
            name='sip_id',
        ),
        migrations.AddField(
            model_name='log',
            name='from_number',
            field=models.CharField(max_length=256, null=True, verbose_name='Номер вызывающего'),
        ),
        migrations.AddField(
            model_name='log',
            name='to_number',
            field=models.CharField(max_length=256, null=True, verbose_name='Номер вызываемого'),
        ),
        migrations.AlterField(
            model_name='log',
            name='event',
            field=models.CharField(max_length=32, verbose_name='Тип звонка'),
        ),
    ]
