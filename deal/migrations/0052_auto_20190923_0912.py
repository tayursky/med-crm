# Generated by Django 2.2.1 on 2019-09-23 09:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('deal', '0051_auto_20190921_1417'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dealcomment',
            name='client',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='deal.Client', verbose_name='Клиент'),
        ),
        migrations.AlterField(
            model_name='historicaldealcomment',
            name='client',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='deal.Client', verbose_name='Клиент'),
        ),
    ]
