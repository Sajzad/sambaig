# Generated by Django 3.1.4 on 2022-06-01 20:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('facebook', '0015_auto_20220527_0150'),
        ('responder', '0077_sentautoresponse_contact'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sentautoresponse',
            name='contact',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='facebook.facebooklead'),
        ),
    ]
