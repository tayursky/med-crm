# Generated by Django 2.2.1 on 2019-07-23 13:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('deal', '0016_auto_20190723_1315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='created_user',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='expenses', to='company.User', verbose_name='Создал запись'),
        ),
    ]
