# Generated by Django 4.2.7 on 2024-01-01 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collector', '0009_entry_original_entry'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='amusewiki_formats',
            field=models.JSONField(null=True),
        ),
    ]