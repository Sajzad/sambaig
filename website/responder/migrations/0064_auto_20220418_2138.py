# Generated by Django 3.1.4 on 2022-04-18 21:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('responder', '0063_autoresponse_gif_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inoutsms',
            name='autoresponse',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='responder.autoresponse'),
        ),
    ]
