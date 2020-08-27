Flask-Babel
===========

.. module:: flask_babel

Flask-Babel is an extension to `Flask`_ that adds i18n and l10n support to
any Flask application with the help of `babel`_, `pytz`_ and
`speaklater`_.  It has builtin support for date formatting with timezone
support as well as a very simple and friendly interface to :mod:`gettext`
translations.

Installation
------------

Install the extension from PyPi::

    $ pip install Flask-Babel

Please note that Flask-Babel requires Jinja >=2.5.  If you are using an
older version you will have to upgrade or disable the Jinja support 
(see configuration).


Configuration
-------------

To get started all you need to do is to instantiate a :class:`Babel`
object after configuring the application::

    from flask import Flask
    from flask_babel import Babel

    app = Flask(__name__)
    app.config.from_pyfile('mysettings.cfg')
    babel = Babel(app)

To disable jinja support, include ``configure_jinja=False`` in the Babel 
constructor call.  The babel object itself can be used to configure the babel support
further.  Babel has the following configuration values that can be used to
change some internal defaults:

=============================== =============================================
`BABEL_DEFAULT_LOCALE`          The default locale to use if no locale
                                selector is registered.  This defaults
                                to ``'en'``.
`BABEL_DEFAULT_TIMEZONE`        The timezone to use for user facing dates.
                                This defaults to ``'UTC'`` which also is the
                                timezone your application must use internally.
`BABEL_TRANSLATION_DIRECTORIES` A semi-colon (``;``) separated string of
                                absolute and relative (to the `root_path` of
                                the application object) paths to translation
                                folders. Defaults to ``translations``.
`BABEL_DOMAIN`                  The message domain used by the application.
                                Defaults to ``messages``.
=============================== =============================================

For more complex applications you might want to have multiple applications
for different users which is where selector functions come in handy.  The
first time the babel extension needs the locale (locale code/ID) of the
current user it will call a :meth:`~Babel.localeselector` function, and
the first time the timezone is needed it will call a
:meth:`~Babel.timezoneselector` function.

If any of these methods return `None` the extension will automatically
fall back to what's in the config.  Furthermore for efficiency that
function is called only once and the return value then cached.  If you
need to switch the language between a request, you can :func:`refresh` the
cache.

Example selector functions::

    from flask import g, request

    @babel.localeselector
    def get_locale():
        # if a user is logged in, use the locale from the user settings
        user = getattr(g, 'user', None)
        if user is not None:
            return user.locale
        # otherwise try to guess the language from the user accept
        # header the browser transmits.  We support de/fr/en in this
        # example.  The best match wins.
        return request.accept_languages.best_match(['de', 'fr', 'en'])

    @babel.timezoneselector
    def get_timezone():
        user = getattr(g, 'user', None)
        if user is not None:
            return user.timezone

The example above assumes that the current user is stored on the
:data:`flask.g` object.

Jinja Filters
-------------

Several commonly used formatters are added as jinja template filters after
calling `init_app().` For dates and times, these are:

- `<datetime>|datetimeformat` -> `format_datetime`
- `<date>|dateformat` -> `format_date`
- `<time>|timeformat` -> `format_time`
- `<timedelta>|timedeltaformat` -> `format_timedelta`

And for numbers, these are:

- `<number>|numberformat` -> `format_number`
- `<number>|decimalformat` -> `format_decimal`
- `<number>|currencyformat` -> `format_currency`
- `<number>|percentformat` -> `format_percent`
- `<number>|scientificformat` -> `format_scientific`

Formatting Dates
----------------

To format dates you can use the :func:`format_datetime`,
:func:`format_date`, :func:`format_time` and :func:`format_timedelta`
functions.  They all accept a :class:`datetime.datetime` (or
:class:`datetime.date`, :class:`datetime.time` and
:class:`datetime.timedelta`) object as first parameter and then optionally
a format string.  The application should use naive datetime objects
internally that use UTC as timezone.  On formatting it will automatically
convert into the user's timezone in case it differs from UTC.

To play with the date formatting from the console, you can use the
:meth:`~flask.Flask.test_request_context` method:

>>> app.test_request_context().push()

Here some examples:

>>> from flask_babel import format_datetime
>>> from datetime import datetime
>>> format_datetime(datetime(1987, 3, 5, 17, 12))
u'Mar 5, 1987 5:12:00 PM'
>>> format_datetime(datetime(1987, 3, 5, 17, 12), 'full')
u'Thursday, March 5, 1987 5:12:00 PM World (GMT) Time'
>>> format_datetime(datetime(1987, 3, 5, 17, 12), 'short')
u'3/5/87 5:12 PM'
>>> format_datetime(datetime(1987, 3, 5, 17, 12), 'dd mm yyy')
u'05 12 1987'
>>> format_datetime(datetime(1987, 3, 5, 17, 12), 'dd mm yyyy')
u'05 12 1987'

And again with a different language:

>>> app.config['BABEL_DEFAULT_LOCALE'] = 'de'
>>> from flask_babel import refresh; refresh()
>>> format_datetime(datetime(1987, 3, 5, 17, 12), 'EEEE, d. MMMM yyyy H:mm')
u'Donnerstag, 5. M\xe4rz 1987 17:12'

For more format examples head over to the `babel`_ documentation.

Formatting Numbers
------------------

To format numbers you can use the :func:`format_number`,
:func:`format_decimal`, :func:`format_currency`, :func:`format_percent` and :func:`format_scientific`
functions.

To play with the date formatting from the console, you can use the
:meth:`~flask.Flask.test_request_context` method:

>>> app.test_request_context().push()

Here are some examples:

>>> from flask_babel import format_number
>>> format_number(1099)
'1,099'

>>> from flask_babel import format_decimal
>>> format_decimal(1.2346)
u'1.235'

>>> from flask_babel import format_currency
>>> format_currency(1099.98, 'USD')
'$1,099.98'

>>> from flask_babel import format_percent
>>> format_percent(0.34)
'34%'

>>> from flask_babel import format_scientific
>>> format_scientific(10000)
'1E4'

And again with a different language:

>>> app.config['BABEL_DEFAULT_LOCALE'] = 'de'
>>> from flask_babel import refresh; refresh()

>>> format_number(1099)
'1.099'

>>> format_decimal(1.2346)
'1,235'

>>> format_currency(1099.98, 'USD')
'1.099,98\xa0$'

>>> format_percent(0.34)
'34\xa0%'

>>> format_scientific(10000)
'1E4'

For more format examples head over to the `babel`_ documentation.

Using Translations
------------------

The other big part next to date formatting are translations.  For that,
Flask uses :mod:`gettext` together with Babel.  The idea of gettext is
that you can mark certain strings as translatable and a tool will pick all
those up, collect them in a separate file for you to translate.  At
runtime the original strings (which should be English) will be replaced by
the language you selected.

There are two functions responsible for translating: :func:`gettext` and
:func:`ngettext`.  The first to translate singular strings and the second
to translate strings that might become plural.  Here some examples::

    from flask_babel import gettext, ngettext

    gettext(u'A simple string')
    gettext(u'Value: %(value)s', value=42)
    ngettext(u'%(num)s Apple', u'%(num)s Apples', number_of_apples)

Additionally if you want to use constant strings somewhere in your
application and define them outside of a request, you can use a lazy
strings.  Lazy strings will not be evaluated until they are actually used.
To use such a lazy string, use the :func:`lazy_gettext` function::

    from flask_babel import lazy_gettext

    class MyForm(formlibrary.FormBase):
        success_message = lazy_gettext(u'The form was successfully saved.')

So how does Flask-Babel find the translations?  Well first you have to
create some.  Here is how you do it:

Translating Applications
------------------------

First you need to mark all the strings you want to translate in your
application with :func:`gettext` or :func:`ngettext`.  After that, it's
time to create a ``.pot`` file.  A ``.pot`` file contains all the strings
and is the template for a ``.po`` file which contains the translated
strings.  Babel can do all that for you.

First of all you have to create a mapping file. For typical Flask applications,
this is what you want in there:

.. sourcecode:: ini

    [python: **.py]
    [jinja2: **/templates/**.html]
    extensions=jinja2.ext.autoescape,jinja2.ext.with_

Save it as ``babel.cfg`` or something similar next to your application.
Then it's time to run the `pybabel` command that comes with Babel to
extract your strings::

    $ pybabel extract -F babel.cfg -o messages.pot .

If you are using the :func:`lazy_gettext` function you should tell pybabel
that it should also look for such function calls::

    $ pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot .

This will use the mapping from the ``babel.cfg`` file and store the
generated template in ``messages.pot``.  Now we can create the first
translation.  For example to translate to German use this command::

    $ pybabel init -i messages.pot -d translations -l de

``-d translations`` tells pybabel to store the translations in a directory
called "translations".  This is the default folder where Flask-Babel will look
for translations unless you changed `BABEL_TRANSLATION_DIRECTORIES` and should
be at the root of your application.

Now edit the ``translations/de/LC_MESSAGES/messages.po`` file as needed.
Check out some gettext tutorials if you feel lost.

To compile the translations for use, ``pybabel`` helps again::

    $ pybabel compile -d translations

What if the strings change?  Create a new ``messages.pot`` like above and
then let ``pybabel`` merge the changes::

    $ pybabel update -i messages.pot -d translations

Afterwards some strings might be marked as fuzzy (where it tried to figure
out if a translation matched a changed key).  If you have fuzzy entries,
make sure to check them by hand and remove the fuzzy flag before
compiling.

Troubleshooting
---------------

On Snow Leopard pybabel will most likely fail with an exception.  If this
happens, check if this command outputs UTF-8::

    $ echo $LC_CTYPE
    UTF-8

This is a OS X bug unfortunately.  To fix it, put the following lines into
your ``~/.profile`` file::

    export LC_CTYPE=en_US.utf-8

Then restart your terminal.

API
---

This part of the documentation documents each and every public class or
function from Flask-Babel.

Configuration
`````````````

.. autoclass:: Babel
   :members:

Context Functions
`````````````````

.. autofunction:: get_translations

.. autofunction:: get_locale

.. autofunction:: get_timezone

Datetime Functions
``````````````````

.. autofunction:: to_user_timezone

.. autofunction:: to_utc

.. autofunction:: format_datetime

.. autofunction:: format_date

.. autofunction:: format_time

.. autofunction:: format_timedelta

Number Functions
``````````````````

.. autofunction:: format_number

.. autofunction:: format_decimal

.. autofunction:: format_currency

.. autofunction:: format_percent

.. autofunction:: format_scientific

Gettext Functions
`````````````````

.. autofunction:: gettext

.. autofunction:: ngettext

.. autofunction:: pgettext

.. autofunction:: npgettext

.. autofunction:: lazy_gettext

.. autofunction:: lazy_pgettext

Low-Level API
`````````````

.. autofunction:: refresh

.. autofunction:: force_locale


.. _Flask: http://flask.pocoo.org/
.. _babel: http://babel.edgewall.org/
.. _pytz: http://pytz.sourceforge.net/
.. _speaklater: http://pypi.python.org/pypi/speaklater
