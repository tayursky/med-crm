# Generated by Django 2.2.1 on 2019-12-28 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0020_auto_20191228_1036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='branch',
            name='managers',
            field=models.ManyToManyField(blank=True, limit_choices_to={'account__is_active': True}, related_name='managers', to='company.Manager', verbose_name='Администраторы'),
        ),
    ]
