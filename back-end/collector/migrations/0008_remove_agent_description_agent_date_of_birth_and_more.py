# Generated by Django 5.0.8 on 2024-10-03 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collector', '0007_general_page'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='agent',
            name='description',
        ),
        migrations.AddField(
            model_name='agent',
            name='date_of_birth',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='agent',
            name='date_of_death',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='agent',
            name='middle_name',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='agent',
            name='place_of_birth',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='agent',
            name='place_of_death',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='agent',
            name='first_name',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='agent',
            name='last_name',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]