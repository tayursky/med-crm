# Generated by Django 2.2.1 on 2019-12-28 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0021_auto_20191228_1241'),
    ]

    operations = [
        migrations.AlterField(
            model_name='branch',
            name='managers',
            field=models.ManyToManyField(blank=True, limit_choices_to={'account__is_active': True}, related_name='managers', to='company.User', verbose_name='Администраторы'),
        ),
    ]
