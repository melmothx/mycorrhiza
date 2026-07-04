#!/bin/bash

set -e
source $HOME/venv/bin/activate
cd $(dirname $0)
cd ../back-end
./manage.py harvest
./manage.py librarycheck
