# Generated by Django 5.1.5 on 2025-02-12 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metrics_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='metrics',
            name='stock',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
