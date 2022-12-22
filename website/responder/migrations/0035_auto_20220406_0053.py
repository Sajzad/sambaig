# Generated by Django 3.1.4 on 2022-04-06 00:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('facebook', '0006_auto_20220328_0256'),
        ('responder', '0034_auto_20220404_1413'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ani',
            name='campaign',
        ),
        migrations.AddField(
            model_name='ani',
            name='contact',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='facebook.adform'),
        ),
    ]
