# Generated by Django 3.1.4 on 2022-03-28 00:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook', '0004_auto_20220321_0038'),
    ]

    operations = [
        migrations.AddField(
            model_name='facebooklead',
            name='to_reply',
            field=models.BooleanField(default=False),
        ),
    ]
