# Generated by Django 4.2.6 on 2023-10-25 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coffee_machine', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='price',
            field=models.FloatField(),
        ),
    ]
