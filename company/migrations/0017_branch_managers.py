# Generated by Django 2.2.1 on 2019-12-25 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0016_auto_20191109_0838_user_is_staff'),
    ]

    operations = [
        migrations.AddField(
            model_name='branch',
            name='managers',
            field=models.ManyToManyField(blank=True, related_name='managers', to='company.User', verbose_name='Администраторы'),
        ),
    ]