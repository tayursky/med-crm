from django.db import migrations


def set_referrer(apps, schema_editor):
    for person in apps.get_model("identity", "person").objects.all().exclude(cache__mlm_parent=None):
        person.cache.update(dict(
            mlm_referrer=person.cache.get('mlm_parent')
        ))
        person.cache.pop('mlm_parent', None)
        person.save()
        print(person.id)


class Migration(migrations.Migration):
    dependencies = [
        ('mlm', '0047_auto_20200125_0851'),
    ]

    operations = [
        migrations.RunPython(set_referrer),
    ]
