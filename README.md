# Installation on Debian 13 Trixie

A full installation has 4 back-end components: Django + Celery,
Mojolicious + Minion.

The suggested/tested approach is to install the Perl modules from the
distro, while keeping python in a virtual env.

```
# apt install build-essential python3-venv libpq-dev rabbitmq-server nginx \
    postgresql libmojolicious-perl libmojo-pg-perl libdbd-pg-perl libminion-perl \
    libdata-dumper-concise-perl libbusiness-isbn-perl libdatetime-perl \
    libpython3-dev
# wget https://deb.amusewiki.org/amusewiki-archive-keyring-trixie_1.0.0_all.deb
# dpkg -i amusewiki-archive-keyring-trixie_1.0.0_all.deb
# apt update
# apt install libtext-amuse-compile-perl
```

Make rabbitmq listen to localhost only:

```
--- a/rabbitmq/rabbitmq-env.conf
+++ b/rabbitmq/rabbitmq-env.conf
@@ -7,7 +7,7 @@
 # By default RabbitMQ will bind to all interfaces, on IPv4 and IPv6 if
 # available. Set this if you only want to bind to one network interface or
 # address family.
-#NODE_IP_ADDRESS=127.0.0.1
+NODE_IP_ADDRESS=127.0.0.1
 
 # Defaults to 5672.
 #NODE_PORT=5672
```

Create a dedicated user

```
adduser mycorrhiza --disabled-password
```

Under mycorrhiza user, clone the repo and initialize the virtual env

```
mkdir static
python3 -m venv ~/venv
source ~/venv/bin/activate
echo "source ~/venv/bin/activate" >> .profile
git clone https://github.com/melmothx/mycorrhiza.git
cd mycorrhiza/back-end
pip install -r requirements.txt
pip install uwsgi
bin/install_xapian 2.0.0
```

Create a postgresql database:

```
# su - postgres
$ psql
postgres=# create user mycorrhiza with password 'MY PASSWORD';
postgres=# create database mycorrhiza owner mycorrhiza;
```

Create a AMPQ user/virtual host.

```
# rabbitmqctl add_user mycorrhiza 'MY PASSWORD'
# rabbitmqctl add_vhost mycorrhiza
# rabbitmqctl set_permissions -p mycorrhiza mycorrhiza ".*" ".*" ".*"
```

## Django application


Create the local settings file `back-end/local_settings.py` and
populate it with your hostnames and passwords.

```
ALLOWED_HOSTS = ['my.hostname.org' ]
SECRET_KEY = 'A LONG RANDOM STRING'
DATABASES = {
     'default': {
         'ENGINE': 'django.db.backends.postgresql',
         'NAME': 'mycorrhiza',
         'USER': 'mycorrhiza',
         'PASSWORD': 'MY PASSWORD',
         'HOST': 'localhost',
         'PORT': '5432',
   }
}
STATIC_ROOT = "/home/mycorrhiza/static"
DEBUG = False
CANONICAL_ADDRESS = 'https://my.hostname.org'
MYCORRHIZA_EMAIL_FROM  = 'noreply@my.hostname.org'
AMUSECOMPILE_API_KEY = "STRONG RANDOM KEY"
AMUSECOMPILE_URL = "http://127.0.0.1:9500/api/v1"
CELERY_BROKER_URL = 'amqp://mycorrhiza:AMPQPASSWORD@localhost:5672/mycorrhiza'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
MYCORRHIZA_NOTIFICATIONS_EMAIL = [
    "notifications@myhostname",
]
WIKIDATA_TOKEN = 'your wikidata token, if you have one' 
```

Run `./manage.py collectstatic`

If you are migrating an instance, load the DB, otherwise run:

```
python manage.py migrate
python manage.py createsuperuser
```

Check if it starts:

```
python manage.py runserver
```

And create the a uwsgi wrapper:

```
#!/bin/bash

source $HOME/venv/bin/activate
mkdir -p $HOME/var
echo "Starting up..."
uwsgi --chdir=$HOME/mycorrhiza/back-end \
      --module=mycorrhiza.wsgi:application \
      --env DJANGO_SETTINGS_MODULE=mycorrhiza.settings \
      --master \
      --cheap \
      --socket=$HOME/var/mycorrhiza.socket \
      --chmod-socket=666 \
      --pidfile=$HOME/var/mycorrhiza.pid \
      --processes=5 \
      --harakiri=6000 \
      --max-requests=50
```


## Mojolicious application

Create the file `amusecompile/amusecompile.yml`

```
hypnotoad:
  workers: 3
  listen:
    - 'http://127.0.0.1:9500'
admin_passwords:
  - admin:PASSWORD
secrets:
  - RANDOM SECRET
api_keys:
  - THE AMUSECOMPILE_API_KEY ABOVE
dbi_connection_string: "postgresql://mycorrhiza:PGPASSWORD-AS-ABOVE@localhost:5432/mycorrhiza"
```

And check if it starts:

```
script/amusecompile  daemon
```

## Systemd Unit files

