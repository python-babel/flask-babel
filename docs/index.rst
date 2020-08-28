Flask-Babel
===========

.. module:: flask_babel

Easy integration of `Flask`_ and `babel`_.

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
constructor call.  The babel object itself can be used to configure the babel
support further.  Babel has the following configuration values that can be used
to change some internal defaults:

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
    def get_user_locale():
        # if a user is logged in, use the locale from the user settings
        user = getattr(g, 'user', None)
        if user is not None:
            return user.locale
        # otherwise try to guess the language from the user accept
        # header the browser transmits.  We support de/fr/en in this
        # example.  The best match wins.
        return request.accept_languages.best_match(['de', 'fr', 'en'])

    @babel.timezoneselector
    def get_user_timezone():
        user = getattr(g, 'user', None)
        if user is not None:
            return user.timezone

The example above assumes that the current user is stored on the
:data:`flask.g` object.

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

Dates, Times, and Numbers
-------------------------
Babel provides many utilities for dealing with dates, times, and numbers
beyond what the built-in Python `gettext`_ module supports. You can easily
use these with Flask-Babel::

    from datetime import datetime
    from babel.numbers import format_decimal
    from babel.dates import format_datetime
    from flask_babel import get_locale, get_timezone

    @app.route('/currency')
    def currency():
        return format_currency(1000.99, 'CAD', locale=get_locale())

    @app.route('/date')
    def date():
        return format_datetime(
            datetime.utcnow(),
            'H:mm zzzz',
            tzinfo=get_timezone(),
            locale=get_locale()
        )

All of the formatting methods in babel.numbers and .dates take a `locale`
parameter, which we populate with our Flask-Babel `get_locale()`.

.. note::

   Prior to version 3.0.0, every Babel `format_*` method was duplicated in
   Flask-Babel, which was needless duplication and meant that Flask-Babel
   was always out of date with changes in Babel. Instead, we just provide
   the glue and you (the user) just import directly from babel. This is the
   same approach that other integrations such as Flask-WTF started using.

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
.. _gettext: https://docs.python.org/3/library/gettext.html
