#!/bin/bash

set -e

cd $(dirname $0)
cd ../../front-end
../utils/bin/create_pot.pl src --pot src/i18n/messages.pot
