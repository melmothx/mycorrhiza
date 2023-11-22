# Installation

Setup the python virtualenv.

Then run:

```
pip install -r requirements.txt
bin/install_xapian.sh 1.4.22
```

Create `local_settings.py` in the root of the project with at least:

```
ALLOWED_HOSTS = ['.amusewiki.org', 'other-host.example.org' ]
SECRET_KEY = 'MyLongSecretKey'
```

The application is going to use sqlite3 by default (see below for
other databases).

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

## MySQL

```
apt install libmariadbclient-dev libmariadb-dev-compat
```

Put credentials in `$HOME/.my.cnf`

```
import os
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            "read_default_file": os.path.join(os.environ['HOME'], ".my.cnf"),
            "sql_mode": "STRICT_TRANS_TABLES",
            "init_command": "SET default_storage_engine=INNODB",
        }
    }
}
```


