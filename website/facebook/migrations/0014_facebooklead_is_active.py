# Generated by Django 3.1.4 on 2022-05-27 01:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook', '0013_auto_20220524_1916'),
    ]

    operations = [
        migrations.AddField(
            model_name='facebooklead',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]
