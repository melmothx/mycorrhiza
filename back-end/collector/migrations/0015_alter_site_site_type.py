# Generated by Django 5.1.6 on 2025-02-14 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collector', '0014_libraryerrorreport'),
    ]

    operations = [
        migrations.AlterField(
            model_name='site',
            name='site_type',
            field=models.CharField(choices=[('amusewiki', 'Amusewiki'), ('generic', 'Generic OAI-PMH'), ('koha-marc21', 'KOHA MARC21'), ('koha-unimarc', 'KOHA UNIMARC'), ('csv', 'CSV Upload'), ('calibretree', 'Calibre File Tree')], default='generic', max_length=32),
        ),
    ]
