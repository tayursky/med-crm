# Generated by Django 2.2.1 on 2020-02-11 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deal', '0104_auto_20200112_0908'),
    ]

    operations = [
        migrations.AddField(
            model_name='deal',
            name='status',
            field=models.CharField(choices=[('in_work', 'В работе'), ('closed', 'Закрыта')], default='in_work', max_length=32, verbose_name='Статус сделки'),
        ),
        migrations.AddField(
            model_name='historicaldeal',
            name='status',
            field=models.CharField(choices=[('in_work', 'В работе'), ('closed', 'Закрыта')], default='in_work', max_length=32, verbose_name='Статус сделки'),
        ),
    ]
