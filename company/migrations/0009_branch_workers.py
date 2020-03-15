# Generated by Django 2.2.1 on 2019-10-25 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('identity', '0016_auto_20191011_1527'),
        ('company', '0008_manager_master'),
    ]

    operations = [
        migrations.AddField(
            model_name='branch',
            name='workers',
            field=models.ManyToManyField(related_name='workers', to='identity.Person', verbose_name='Персонал'),
        ),
    ]
