Flask ICU
=========

[![Build Status](https://travis-ci.org/beavyHQ/flask-icu.svg?branch=retrofit-for-pyicu)](https://travis-ci.org/beavyHQ/flask-icu)

Implements i18n and l10n support for Flask using the industry standard
ICU and pytz.


Extracting messages for tests:


First time:
pybabel extract -F babel.cfg -k format -o messages.pot .
pybabel init -i messages.pot -d translations -l en
pybabel init -i messages.pot -d translations -l de
../../node_modules/.bin/po2json po_translations/en/LC_MESSAGES/messages.po translations/en/messages.json -f mf --fallback-to-msgid
../../node_modules/.bin/po2json po_translations/de/LC_MESSAGES/messages.po translations/de/messages.json -f mf


pybabel update -i messages.pot -d translations

