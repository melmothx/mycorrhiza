# Installation

Setup the python virtualenv (`python3 -m venv DIRECTORY`)

Then run:

```
pip install -r requirements.txt
bin/install_xapian.sh 1.4.24
```

Setup a PostgreSQL server, that's what Mycorrhiza needs.

Create `local_settings.py` in the root of the project with:

```
ALLOWED_HOSTS = ['.amusewiki.org', 'other-host.example.org' ]
SECRET_KEY = 'MyLongSecretKey'
DATABASES = {
     'default': {
         'ENGINE': 'django.db.backends.postgresql',
         'NAME': 'mycorrhiza',
         'USER': 'mycorrhiza',
         'PASSWORD': "MyPassword",
         'HOST': 'localhost',
         'PORT': '5432',
   }
}
STATIC_ROOT = "/home/mycorrhiza/static"
DEBUG = False
CANONICAL_ADDRESS = "https://my.host.org"
MYCORRHIZA_EMAIL_FROM  = "noreply@my.host.org"
```


Run:

```
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

With the superuser you created you can now access the admin at
`http://127.0.0.1:8000/admin`. Add a site with OAI-PMH (provide the
OAI-PMH endpoint in the Url field) to harvest.

Run:

```
python manage.py harvest
```

Now `http://127.0.0.1:8000/admin` should be working.

The `MEDIA_ROOT` should not be exposed to the webserver. The only
uploads we have are CSV which should not be public.
