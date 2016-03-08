# -*- coding: utf-8 -*-
"""
    flaskext.icu
    ~~~~~~~~~~~~

    Implements i18n/l10n support for Flask applications based on PyICU. The
    interface is derived from [Flask-Babel](https://pythonhosted.org/Flask-Babel/).

    :copyright: (c) 2016 by Ethan Miller (based on Flask-Babel)
    :license: BSD, see LICENSE for more details.
"""
from __future__ import absolute_import
import os
import json

from datetime import datetime
from decimal import Decimal
from flask import _request_ctx_stack
from icu import (Locale, MessageFormat, DateFormat, SimpleDateFormat,
                 Formattable, TimeZone, ICUtzinfo, NumberFormat, DecimalFormat)
from werkzeug import ImmutableDict

from flask_icu._compat import string_types

TRANSLATIONS_PATH = 'translations'

class ICU(object):
    """Central controller class that can be used to configure how
    Flask-ICU behaves. Each application that wants to use Flask-ICU
    has to create, or run :meth:`init_app` on, an instance of this class
    after the configuration was initialized.
    """

    messages = {}

    icu_date_formats = ImmutableDict({
        'short':        DateFormat.SHORT,
        'medium':       DateFormat.MEDIUM,
        'long':         DateFormat.LONG,
        'full':         DateFormat.FULL,
    })

    default_date_formats = ImmutableDict({
        'time':             'medium',
        'date':             'medium',
        'datetime':         'medium',
        'time.short':       None,
        'time.medium':      None,
        'time.full':        None,
        'time.long':        None,
        'date.short':       None,
        'date.medium':      None,
        'date.full':        None,
        'date.long':        None,
        'datetime.short':   None,
        'datetime.medium':  None,
        'datetime.full':    None,
        'datetime.long':    None,
    })

    def __init__(self, app=None, default_locale='en', default_timezone='UTC',
                 date_formats=None, configure_jinja=True):
        self._default_locale = default_locale
        self._default_timezone = default_timezone
        self._date_formats = date_formats
        self._configure_jinja = configure_jinja
        self.app = app

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Set up this instance for use with *app*, if no app was passed to
        the constructor.
        """
        self.app = app
        app.icu_instance = self
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['icu'] = self

        app.config.setdefault('ICU_DEFAULT_LOCALE', self._default_locale)
        app.config.setdefault('ICU_DEFAULT_TIMEZONE', self._default_timezone)
        if self._date_formats is None:
            self._date_formats = self.default_date_formats.copy()

        #: A mapping of ICU datetime format strings that can be modified
        #: to change the defaults.  If you invoke :func:`format_datetime`
        #: and do not provide any format string Flask-ICU will do the
        #: following things:
        #:
        #: 1.   look up ``date_formats['datetime']``.  By default ``'medium'``
        #:      is returned to enforce medium length datetime formats.
        #: 2.   ``date_formats['datetime.medium'] (if ``'medium'`` was
        #:      returned in step one) is looked up.  If the return value
        #:      is anything but `None` this is used as new format string.
        #:      otherwise the default for that language is used.
        self.date_formats = self._date_formats

        self.locale_selector_func = None
        self.timezone_selector_func = None

        if self._configure_jinja:
            app.jinja_env.globals.update(
                format=format,
                format_date=format_date,
                format_time=format_time,
                format_datetime=format_datetime,
                format_number=format_number,
                format_decimal=format_decimal,
                format_scientific=format_scientific,
                format_percent=format_percent)

    def localeselector(self, f):
        """Registers a callback function for locale selection.  The default
        behaves as if a function was registered that returns `None` all the
        time.  If `None` is returned, the locale falls back to the one from
        the configuration.

        This has to return the locale as string (eg: ``'de_AT'``, ''`en_US`'')
        """
        assert self.locale_selector_func is None, \
            'a localeselector function is already registered'
        self.locale_selector_func = f
        return f

    def timezoneselector(self, f):
        """Registers a callback function for timezone selection.  The default
        behaves as if a function was registered that returns `None` all the
        time.  If `None` is returned, the timezone falls back to the one from
        the configuration.

        This has to return the timezone as string (eg: ``'Europe/Vienna'``)
        """
        assert self.timezone_selector_func is None, \
            'a timezoneselector function is already registered'
        self.timezone_selector_func = f
        return f


    def list_translations(self):
        """Returns a list of all the locales translations exist for.  The
        list returned will be filled with actual locale objects and not just
        strings.
        """
        dirname = os.path.join(self.app.root_path, TRANSLATIONS_PATH)
        if not os.path.isdir(dirname):
            return []
        return [name for name in os.listdir(dirname)
            if os.path.isdir(os.path.join(dirname, name))]

    @property
    def default_locale(self):
        """The default locale from the configuration as instance of a
        `icu.Locale` object.
        """
        default = self.app.config['ICU_DEFAULT_LOCALE']
        if default is None:
            default = 'en'
        return Locale(default)

    @property
    def default_timezone(self):
        """The default timezone from the configuration as instance of a
        `icu.TimeZone` object.
        """
        default = self.app.config['ICU_DEFAULT_TIMEZONE']
        if default is None:
            default = 'UTC'
        return (ICUtzinfo.getInstance(default).timezone)

def load_messages(locale):
    """Loads ICU messages for a given locale from the source files. Translation
    files must be located in path: '<root>/translations/<lang>/'.
    """
    ctx = _request_ctx_stack.top
    if ctx is None:
        return None
    dirname = os.path.join(ctx.app.root_path, TRANSLATIONS_PATH)
    if not os.path.isdir(dirname):
        raise Exception('Unable to find the translations path.')
    locales_list = [name for name in os.listdir(dirname)
                    if os.path.isdir(os.path.join(dirname, name))]
    messages = {}
    if locale not in locales_list:
        raise Exception('No locale ICU message files found for the locale: {}'.format(locale))
    else:
        for subdir, dirs, files in os.walk(dirname + '/' + locale):
            for file in files:
                with open(subdir + '/' + file) as data_file:
                    data = json.load(data_file)
                    messages.update(data)
    return messages


def get_message(key):
    """Returns an ICU format message string for the given key."""
    ctx = _request_ctx_stack.top
    if ctx is None:
        return None
    messages = getattr(ctx, 'icu_messages', None)
    if messages is None:
        messages = get_messages()
    # if key in messages:
    #     msg = messages[key]
    # else:
    #     msg = key
    try:
        return messages[key]
    except KeyError:
        return key


def get_messages():
    """Returns the correct icu message set that should be used for
    this request. This will never fail and returns 'None' if used
    outside of the request or if a message cannot be found.
    """
    ctx = _request_ctx_stack.top
    if ctx is None:
        return None
    messages = getattr(ctx, 'icu_messages', None)
    if messages is None:
        locale = get_locale()
        messages = load_messages(locale.getName())
        ctx.icu_messages = messages
    return messages


def get_locale():
    """Returns the locale that should be used for this request as
    `icu.Locale` object.  Returns `None` if used outside of
    a request.
    """
    ctx = _request_ctx_stack.top
    if ctx is None:
        return None
    locale = getattr(ctx, 'icu_locale', None)
    if locale is None:
        icu = ctx.app.extensions['icu']
        if icu.locale_selector_func is None:
            locale = icu.default_locale
        else:
            rv = icu.locale_selector_func()
            if rv is None:
                locale = icu.default_locale
            else:
                locale = Locale(rv)
        ctx.icu_locale = locale
    return locale


def get_timezone():
    """Returns the timezone that should be used for this request as
    `an icu.TimeZone` object.  Returns `None` if used outside of
    a request.
    """
    ctx = _request_ctx_stack.top
    tzinfo = getattr(ctx, 'icu_tzinfo', None)
    if tzinfo is None:
        icu = ctx.app.extensions['icu']
        if icu.timezone_selector_func is None:
            tzinfo = icu.default_timezone
        else:
            rv = icu.timezone_selector_func()
            if rv is None:
                tzinfo = icu.default_timezone
            else:
                if isinstance(rv, string_types):
                    tzinfo = TimeZone.createTimeZone(rv)
                else:
                    tzinfo = rv
        ctx.icu_tzinfo = tzinfo
    return tzinfo


def icu_refresh():
    """Refreshes the cached timezones and locale information.  This can
    be used to switch a translation between a request and if you want
    the changes to take place immediately, not just with the next request::

        user.timezone = request.form['timezone']
        user.locale = request.form['locale']
        icu_refresh()
        flash(format('Language was changed'))

    Without that refresh, the :func:`~flask.flash` function would probably
    return English text and a now German page.
    """
    ctx = _request_ctx_stack.top
    for key in 'icu_locale', 'icu_tzinfo', 'icu_translations':
        if hasattr(ctx, key):
            delattr(ctx, key)


def format_datetime(datetime=None, format=None, rebase=True):
    """Return a date formatted according to the given pattern.  If no
    :class:`~datetime.datetime` object is passed, the current time is
    assumed.  By default rebasing happens which causes the object to
    be converted to the users's timezone.  This function formats both
    date and time.

    The format parameter can either be ``'short'``, ``'medium'``,
    ``'long'`` or ``'full'`` (in which cause the language's default for
    that setting is used, or the default from the :attr:`Babel.date_formats`
    mapping is used) or a format string as documented by Babel.

    This function is also available in the template context as filter
    named `datetimeformat`.
    """
    return _date_format(datetime, rebase, 'datetime', format)


def format_date(date=None, format=None, rebase=True):
    """Return a date formatted according to the given pattern.  If no
    :class:`~datetime.datetime` or :class:`~datetime.date` object is passed,
    the current time is assumed.  By default rebasing happens which causes
    the object to be converted to the users's timezone (as returned by
    :func:`to_user_timezone`).  This function only formats the date part
    of a :class:`~datetime.datetime` object.

    The format parameter can either be ``'short'``, ``'medium'``,
    ``'long'`` or ``'full'`` (in which cause the language's default for
    that setting is used, or the default from the :attr:`Babel.date_formats`
    mapping is used) or a format string as documented by Babel.

    This function is also available in the template context as filter
    named `dateformat`.
    """
    return _date_format(date, rebase, 'date', format)


def format_time(time=None, format=None, rebase=True):
    """Return a time formatted according to the given pattern.  If no
    :class:`~datetime.datetime` object is passed, the current time is
    assumed.  By default rebasing happens which causes the object to
    be converted to the users's timezone (as returned by
    :func:`to_user_timezone`).  This function formats both date and
    time.

    The format parameter can either be ``'short'``, ``'medium'``,
    ``'long'`` or ``'full'`` (in which cause the language's default for
    that setting is used, or the default from the :attr:`Babel.date_formats`
    mapping is used) or a format string as documented by Babel.

    This function is also available in the template context as filter
    named `timeformat`.
    """
    return _date_format(time, rebase, 'time', format)


def _date_format(datetime, rebase, datetime_type, format):
    """Internal helper that looks up and creates the correct DateFormat
    object, and then uses it to format the date string and return it.
    If rebase is set to true, it automatically reformats the time to the
    user's timezone.
    """
    locale = get_locale()
    icu = _request_ctx_stack.top.app.extensions['icu']
    is_custom = False
    if format is None:
        format = icu.date_formats[datetime_type]
    if format in ('short', 'medium', 'long', 'full'):
        tmp = icu.date_formats["{0}.{1}".format(datetime_type, format)]
        is_custom = False if tmp is None else True
        format = tmp if is_custom else icu.icu_date_formats[format]
    if is_custom:
        formatter = SimpleDateFormat(format, locale)
    else:
        if datetime_type == 'time':
            formatter = DateFormat.createTimeInstance(format, locale)
        if datetime_type == 'date':
            formatter = DateFormat.createDateInstance(format, locale)
        if datetime_type == 'datetime':
            formatter = DateFormat.createDateTimeInstance(format, format, locale)
    if rebase:
        formatter.setTimeZone(get_timezone())
    return formatter.format(datetime)


def format_number(number):
    """Return the given number formatted for the locale in request

    :param number: the number to format
    :return: the formatted number
    :rtype: unicode
    """
    return NumberFormat.createInstance(get_locale()).format(number)


# TODO: Enable a custom 'format' argment on this method like in flask-babel?
def format_decimal(number):
    """Return the given decimal number formatted for the locale in request

    :param number: the number to format
    :return: the formatted number
    :rtype: unicode
    """
    locale = get_locale()
    formatter = DecimalFormat.createInstance(locale)
    if type(number) is Decimal:
        number = float(number)
    return formatter.format(number)


# TODO: Enable a custom 'format' argment on this method like in flask-babel?
def format_currency(number, currency=None):
    """Return the given number formatted for the locale in request

    :param number: the number to format
    :param currency: the currency code
    :return: the formatted number
    :rtype: unicode
    """
    locale = get_locale()
    formatter = NumberFormat.createCurrencyInstance(locale)
    if currency is not None:
        formatter.setCurrency(currency)
    return formatter.format(number).replace('\xa0', '')


# TODO: Enable a custom 'format' argment on this method like in flask-babel?
def format_percent(number):
    """Return formatted percent value for the locale in request

    :param number: the number to format
    :param format: the format to use
    :return: the formatted percent number
    :rtype: unicode
    """
    locale = get_locale()
    formatter = NumberFormat.createPercentInstance(locale)
    return formatter.format(number).replace('\xa0', '')

# TODO: Enable a custom 'format' argment on this method like in flask-babel?
def format_scientific(number):
    """Return value formatted in scientific notation for the locale in request

    :param number: the number to format
    :param format: the format to use
    :return: the formatted percent number
    :rtype: unicode
    """
    locale = get_locale()
    formatter = NumberFormat.createScientificInstance(locale)
    return formatter.format(number)


def format(string, values=None):
    """Translates a string with the given current locale"""

    ctx = _request_ctx_stack.top
    locale = get_locale()
    icu_msg = get_message(string)
    msg = MessageFormat(icu_msg)
    if values is not None:
        keys = []
        vals = []
        for (k, v) in values.items():
            keys.append(k)
            vals.append(Formattable(v))
        return msg.format(keys, vals)
    return msg.format('')
