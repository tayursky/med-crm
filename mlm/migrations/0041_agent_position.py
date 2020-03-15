# Generated by Django 2.2.1 on 2020-01-22 13:13

from django.db import migrations


def set_position(apps, schema_editor):
    apps.get_model("mlm", "agent").objects.filter(pretender=True).update(position='pretender')
    apps.get_model("mlm", "agent").objects.filter(pretender=False).update(position='agent')


class Migration(migrations.Migration):
    dependencies = [
        ('mlm', '0040_auto_20200122_1309'),
    ]

    operations = [
        migrations.RunPython(set_position),
    ]
