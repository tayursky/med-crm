# Generated by Django 2.2.1 on 2020-02-25 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('identity', '0021_auto_20200222_1523'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalperson',
            name='address',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Адрес регистрации'),
        ),
        migrations.AddField(
            model_name='historicalperson',
            name='passport_issued',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Выдавший орган'),
        ),
        migrations.AddField(
            model_name='historicalperson',
            name='passport_number',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='Паспорт серия и номер'),
        ),
        migrations.AddField(
            model_name='person',
            name='address',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Адрес регистрации'),
        ),
        migrations.AddField(
            model_name='person',
            name='passport_issued',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Выдавший орган'),
        ),
        migrations.AddField(
            model_name='person',
            name='passport_number',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='Паспорт серия и номер'),
        ),
    ]
