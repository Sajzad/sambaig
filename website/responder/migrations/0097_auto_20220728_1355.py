# Generated by Django 3.1.4 on 2022-07-28 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('responder', '0096_inoutsms_dlr'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='gallery/'),
        ),
    ]
