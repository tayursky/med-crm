# Generated by Django 2.2.1 on 2019-08-02 08:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sms', '0004_auto_20190802_0618'),
    ]

    operations = [
        migrations.AddField(
            model_name='sms',
            name='template',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sms', to='sms.SmsTemplate', verbose_name='Шаблон'),
        ),
    ]