# Generated by Django 3.1.4 on 2022-04-15 03:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('responder', '0055_inoutsms_autoresponse'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inoutsms',
            name='order',
        ),
    ]
