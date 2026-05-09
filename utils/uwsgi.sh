#!/bin/bash

cd $(dirname $0)
cd ..
appdir=$(pwd)
appname=$(basename $appdir)

source $HOME/venv/bin/activate
mkdir -p $HOME/var
echo "Starting up..."
uwsgi --chdir=$appdir/back-end \
      --module=mycorrhiza.wsgi:application \
      --env DJANGO_SETTINGS_MODULE=mycorrhiza.settings \
      --master \
      --cheap \
      --socket=$HOME/var/$appname.socket \
      --chmod-socket=666 \
      --pidfile=$HOME/var/$appname.pid \
      --processes=5 \
      --harakiri=6000 \
      --max-requests=50
