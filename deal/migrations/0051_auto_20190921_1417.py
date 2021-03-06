# Generated by Django 2.2.1 on 2019-09-21 14:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('deal', '0050_auto_20190919_1522'),
    ]

    operations = [
        migrations.AddField(
            model_name='dealcomment',
            name='client',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='deal.Client', verbose_name='Сделка'),
        ),
        migrations.AddField(
            model_name='historicaldealcomment',
            name='client',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='deal.Client', verbose_name='Сделка'),
        ),
        migrations.AlterField(
            model_name='dealcomment',
            name='deal',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='deal.Deal', verbose_name='Сделка'),
        ),
    ]
