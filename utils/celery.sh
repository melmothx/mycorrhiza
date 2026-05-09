#!/bin/bash

set -e
cd $(dirname $0)
cd ..
appdir=$(pwd)
appname=$(basename $appdir)
source $HOME/venv/bin/activate
cd $appdir/back-end

if [ ! -f local_settings.py ]; then
    echo "Wrong directory!" >&2
    exit 3
fi
exec celery -A mycorrhiza worker -l INFO -n $appname@$(hostname) -c1
