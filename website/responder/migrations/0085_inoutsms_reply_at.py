# Generated by Django 3.1.4 on 2022-06-11 11:18

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('responder', '0084_auto_20220610_0125'),
    ]

    operations = [
        migrations.AddField(
            model_name='inoutsms',
            name='reply_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2022, 6, 11, 11, 18, 53, 549666)),
            preserve_default=False,
        ),
    ]
