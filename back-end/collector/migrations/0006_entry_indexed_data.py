# Generated by Django 4.2.7 on 2023-12-05 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collector', '0005_agent_created_agent_last_modified_datasource_created_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='indexed_data',
            field=models.JSONField(null=True),
        ),
    ]