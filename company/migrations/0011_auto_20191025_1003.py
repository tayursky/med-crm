# Generated by Django 2.2.1 on 2019-10-25 10:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0010_historicaltimetable_timetable'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicaltimetable',
            name='person',
        ),
        migrations.RemoveField(
            model_name='timetable',
            name='person',
        ),
        migrations.AddField(
            model_name='historicaltimetable',
            name='user',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='company.User', verbose_name='Работник'),
        ),
        migrations.AddField(
            model_name='timetable',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='company.User', verbose_name='Работник'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='branch',
            name='workers',
            field=models.ManyToManyField(related_name='workers', to='company.User', verbose_name='Персонал'),
        ),
    ]
