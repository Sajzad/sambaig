# Generated by Django 3.1.4 on 2022-04-14 01:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('responder', '0053_primarynumber'),
    ]

    operations = [
        migrations.AddField(
            model_name='inoutsms',
            name='is_manual',
            field=models.BooleanField(default=False),
        ),
    ]
