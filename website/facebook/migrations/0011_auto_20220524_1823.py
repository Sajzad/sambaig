# Generated by Django 3.1.4 on 2022-05-24 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook', '0010_facebooklead_is_unsubscribed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facebooklead',
            name='phone',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
    ]
