# Generated by Django 5.0.8 on 2024-08-18 06:02

import collector.models
import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataSource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('oai_pmh_identifier', models.CharField(max_length=2048)),
                ('datestamp', models.DateTimeField(null=True)),
                ('full_data', models.JSONField()),
                ('description', models.TextField(null=True)),
                ('year_edition', models.IntegerField(null=True)),
                ('year_first_edition', models.IntegerField(null=True)),
                ('uri', models.URLField(max_length=2048, null=True)),
                ('uri_label', models.CharField(max_length=2048, null=True)),
                ('content_type', models.CharField(max_length=128, null=True)),
                ('material_description', models.TextField(null=True)),
                ('shelf_location_code', models.CharField(max_length=255, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('is_aggregation', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('code', models.CharField(max_length=4, primary_key=True, serialize=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Library',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('url', models.URLField(blank=True, max_length=255, null=True)),
                ('public', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=True)),
                ('email_public', models.EmailField(blank=True, max_length=254)),
                ('email_internal', models.EmailField(blank=True, max_length=254)),
                ('opening_hours', models.TextField(blank=True)),
                ('latitude', models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True)),
                ('enable_check', models.BooleanField(default=False)),
                ('check_token', models.CharField(blank=True, max_length=255)),
                ('last_check', models.DateTimeField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Libraries',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254)),
                ('library_admin', models.BooleanField(default=False)),
                ('can_merge', models.BooleanField(default=False)),
                ('expiration', models.DateTimeField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('password_reset_token', models.CharField(blank=True, max_length=255, null=True)),
                ('password_reset_expiration', models.DateTimeField(blank=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
                ('libraries', models.ManyToManyField(related_name='affiliated_users', to='collector.library')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('canonical_agent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='variant_agents', to='collector.agent')),
            ],
        ),
        migrations.CreateModel(
            name='AggregationDataSource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sorting_pos', models.IntegerField(null=True)),
                ('aggregated', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aggregation_data_sources', to='collector.datasource')),
                ('aggregation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aggregated_data_sources', to='collector.datasource')),
            ],
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('subtitle', models.CharField(max_length=255, null=True)),
                ('checksum', models.CharField(max_length=255)),
                ('is_aggregation', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('indexed_data', models.JSONField(null=True)),
                ('datestamp', models.DateTimeField(null=True)),
                ('authors', models.ManyToManyField(related_name='authored_entries', to='collector.agent')),
                ('canonical_entry', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='variant_entries', to='collector.entry')),
                ('original_entry', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='translations', to='collector.entry')),
                ('languages', models.ManyToManyField(to='collector.language')),
            ],
            options={
                'verbose_name_plural': 'Entries',
            },
        ),
        migrations.AddField(
            model_name='datasource',
            name='entry',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='collector.entry'),
        ),
        migrations.CreateModel(
            name='AggregationEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aggregated', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aggregation_entries', to='collector.entry')),
                ('aggregation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aggregated_entries', to='collector.entry')),
            ],
            options={
                'verbose_name_plural': 'Aggregation Entries',
            },
        ),
        migrations.CreateModel(
            name='Exclusion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('exclude_author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='collector.agent')),
                ('exclude_entry', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='collector.entry')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exclusions', to=settings.AUTH_USER_MODEL)),
                ('exclude_library', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='collector.library')),
            ],
        ),
        migrations.CreateModel(
            name='ChangeLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255)),
                ('operation', models.CharField(max_length=64)),
                ('comment', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('agent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='changelogs', to='collector.agent')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='changelogs', to=settings.AUTH_USER_MODEL)),
                ('entry', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='changelogs', to='collector.entry')),
                ('exclusion', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='changelogs', to='collector.exclusion')),
            ],
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('url', models.URLField(blank=True, max_length=255)),
                ('last_harvested', models.DateTimeField(blank=True, null=True)),
                ('comment', models.TextField(blank=True)),
                ('oai_set', models.CharField(blank=True, max_length=64, null=True)),
                ('oai_metadata_format', models.CharField(blank=True, choices=[('oai_dc', 'Dublin Core'), ('marc21', 'MARC XML')], max_length=32, null=True)),
                ('site_type', models.CharField(choices=[('amusewiki', 'Amusewiki'), ('generic', 'Generic OAI-PMH'), ('csv', 'CSV Upload'), ('calibretree', 'Calibre File Tree')], default='generic', max_length=32)),
                ('csv_type', models.CharField(blank=True, choices=[('calibre', 'Calibre'), ('abebooks_home_base', 'Abebooks Home Base')], max_length=32, null=True)),
                ('active', models.BooleanField(default=True)),
                ('amusewiki_formats', models.JSONField(null=True)),
                ('tree_path', models.CharField(blank=True, max_length=255, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('library', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sites', to='collector.library')),
            ],
        ),
        migrations.CreateModel(
            name='NameAlias',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_name', models.CharField(choices=[('author', 'Author'), ('title', 'Title'), ('subtitle', 'Subtitle'), ('language', 'Language')], max_length=32)),
                ('value_name', models.CharField(max_length=255)),
                ('value_canonical', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collector.site')),
            ],
            options={
                'verbose_name_plural': 'Name Aliases',
            },
        ),
        migrations.CreateModel(
            name='Harvest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField()),
                ('logs', models.TextField()),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collector.site')),
            ],
        ),
        migrations.AddField(
            model_name='datasource',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collector.site'),
        ),
        migrations.CreateModel(
            name='SpreadsheetUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spreadsheet', models.FileField(upload_to=collector.models.spreadsheet_upload_directory)),
                ('comment', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('replace_all', models.BooleanField(default=False)),
                ('processed', models.DateTimeField(blank=True, null=True)),
                ('error', models.TextField(blank=True, null=True)),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collector.site')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploaded_spreadsheets', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='aggregationdatasource',
            constraint=models.UniqueConstraint(fields=('aggregation', 'aggregated'), name='unique_data_source_aggregation_aggregated'),
        ),
        migrations.AddConstraint(
            model_name='aggregationentry',
            constraint=models.UniqueConstraint(fields=('aggregation', 'aggregated'), name='unique_entry_aggregation_aggregated'),
        ),
        migrations.AddConstraint(
            model_name='namealias',
            constraint=models.UniqueConstraint(fields=('site', 'field_name', 'value_name'), name='unique_site_field_name_value_name'),
        ),
        migrations.AddConstraint(
            model_name='datasource',
            constraint=models.UniqueConstraint(fields=('site', 'oai_pmh_identifier'), name='unique_site_oai_pmh_identifier'),
        ),
    ]