#!/bin/bash

set -e
set -x
i18ndir=src/i18n

cd $(dirname $0)
cd ../../front-end
../utils/bin/create_pot.pl src --pot "$i18ndir/messages.pot"

for i in en it de fr; do
    if [ ! -f "$i18ndir/$i.po" ]; then
        msginit --input="$i18ndir/messages.pot" --output "$i18ndir/$i.po" --locale=$i
    fi
    msgmerge --no-fuzzy-matching --update "$i18ndir/$i.po" "$i18ndir/messages.pot"
done

../utils/bin/compile_po_files.pl $i18ndir $i18ndir/translations.json
