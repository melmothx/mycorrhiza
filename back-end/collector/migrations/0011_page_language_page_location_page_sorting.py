# Generated by Django 5.0.8 on 2024-11-24 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collector', '0010_alter_changelog_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='language',
            field=models.CharField(choices=[('bg', 'Български'), ('cs', 'Čeština'), ('da', 'Dansk'), ('de', 'Deutsch'), ('el', 'Ελληνικά'), ('en', 'English'), ('eo', 'Esperanto'), ('es', 'Español'), ('eu', 'Euskara'), ('fa', 'فارسی'), ('fi', 'Suomi'), ('fr', 'Français'), ('hr', 'Hrvatski'), ('hu', 'Magyar'), ('id', 'Bahasa Indonesia'), ('it', 'Italiano'), ('ja', '日本語'), ('mk', 'Македонски'), ('nl', 'Nederlands'), ('pl', 'Polski'), ('pt', 'Português'), ('ro', 'Română'), ('ru', 'Русский'), ('sq', 'Shqip'), ('sr', 'Srpski'), ('sv', 'Svenska'), ('tl', 'Tagalog'), ('tr', 'Türkçe'), ('uk', 'Українська'), ('zh', '中文')], default='en', max_length=4),
        ),
        migrations.AddField(
            model_name='page',
            name='location',
            field=models.CharField(choices=[('draft', 'Drafts'), ('footer', 'Footer')], default='draft', max_length=16),
        ),
        migrations.AddField(
            model_name='page',
            name='sorting',
            field=models.IntegerField(default=0),
        ),
    ]
