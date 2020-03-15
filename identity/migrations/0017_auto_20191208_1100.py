# Generated by Django 2.2.1 on 2019-12-08 11:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sip', '0006_mightycalluser'),
        ('identity', '0016_auto_20191011_1527'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalperson',
            name='mighty_call_user',
            field=models.ForeignKey(blank=True, db_constraint=False, help_text='Пользователь яндекс телефонии', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sip.MightyCallUser', verbose_name='Яндекс телефония'),
        ),
        migrations.AddField(
            model_name='person',
            name='mighty_call_user',
            field=models.ForeignKey(blank=True, help_text='Пользователь яндекс телефонии', null=True, on_delete=django.db.models.deletion.CASCADE, to='sip.MightyCallUser', verbose_name='Яндекс телефония'),
        ),
        migrations.AlterField(
            model_name='historicalperson',
            name='sip_id',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Манго-офис'),
        ),
        migrations.AlterField(
            model_name='person',
            name='sip_id',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Манго-офис'),
        ),
    ]
