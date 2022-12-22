# Generated by Django 3.1.4 on 2022-04-24 13:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('facebook', '0010_facebooklead_is_unsubscribed'),
        ('responder', '0067_logicresponse_ani'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assigncontact',
            name='contact',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assign_contact', to='facebook.adform'),
        ),
    ]
