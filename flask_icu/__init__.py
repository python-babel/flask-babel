# -*- coding: utf-8 -*-
"""
    # TODO: Change this header 
    flaskext.babel
    ~~~~~~~~~~~~~~

    Implements i18n/l10n support for Flask applications based on PyICU.

    :copyright: (c) 2013 by Armin Ronacher, Daniel Neuhäuser.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import absolute_import
import os
import json

# this is a workaround for a snow leopard bug that babel does not
# work around :)
if os.environ.get('LC_CTYPE', '').lower() == 'utf-8':
    os.environ['LC_CTYPE'] = 'en_US.utf-8'

from datetime import datetime
from flask import _request_ctx_stack
# from babel import dates, numbers, support, Locale
from icu import Locale, MessageFormat, DateFormat, SimpleDateFormat, Formattable, TimeZone, ICUtzinfo
from werkzeug import ImmutableDict
try:
    from pytz.gae import pytz
except ImportError:
    from pytz import timezone, UTC
else:
    timezone = pytz.timezone
    UTC = pytz.UTC

from flask_icu._compat import string_types

import pdb

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

        #: a mapping of Babel datetime format strings that can be modified
        #: to change the defaults.  If you invoke :func:`format_datetime`
        #: and do not provide any format string Flask-Babel will do the
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
            app.jinja_env.globals.update(format=format)

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


    # def list_translations(self):
    #     """Returns a list of all the locales translations exist for.  The
    #     list returned will be filled with actual locale objects and not just
    #     strings.
    #
    #     .. versionadded:: 0.6
    #     """
    #     dirname = os.path.join(self.app.root_path, 'translations')
    #     if not os.path.isdir(dirname):
    #         return []
    #     result = []
    #     for folder in os.listdir(dirname):
    #         locale_dir = os.path.join(dirname, folder, 'LC_MESSAGES')
    #         if not os.path.isdir(locale_dir):
    #             continue
    #         if filter(lambda x: x.endswith('.mo'), os.listdir(locale_dir)):
    #             result.append(Locale.parse(folder))
    #     if not result:
    #         result.append(Locale.parse(self._default_locale))
    #     return result

    @property
    def default_locale(self):
        """The default locale from the configuration as instance of a
        `babel.Locale` object.
        """
        return Locale(self.app.config['ICU_DEFAULT_LOCALE'])

    @property
    def default_timezone(self):
        """The default timezone from the configuration as instance of a
        `pytz.timezone` object.
        """
        return (ICUtzinfo.getInstance(
            self.app.config['ICU_DEFAULT_TIMEZONE']).timezone)

def load_messages(locale):
    """Loads ICU messages for a given locale from the source files. Translation
    files must be located in path pattern: '<root>/translations/<lang>/'.
    """
    ctx = _request_ctx_stack.top
    if ctx is None:
        return None
    dirname = os.path.join(ctx.app.root_path, 'translations')
    # TODO: Handle case where the translations dir is not present
    locales_list = [name for name in os.listdir(dirname)
                    if os.path.isdir(os.path.join(dirname, name))]
    messages = {}
    if locale not in locales_list:
        raise Exception('No locale ICU message files found for the locale: %d'.format(locale))
    else:
        for subdir, dirs, files in os.walk(dirname + '/' + locale):
            for file in files:
                with open(subdir + '/' + file) as data_file:
                    data = json.load(data_file)
                    z = messages.copy()
                    z.update(data)
                    messages = z
    return messages

def get_message(key):
    """Returns a ICU format message string for the given key."""

    ctx = _request_ctx_stack.top
    if ctx is None:
        return None
    messages = getattr(ctx, 'icu_messages', None)
    if messages is None:
        messages = get_messages()
    if key in messages:
        msg = messages[key]
    else:
        msg = key
    return msg

def get_messages():
    """Returns the correct icu message set that should be used for
    this request. This will never fail and return a dummy translation
    object if used outside of the request or if a message cannot be
    found.
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
    `babel.Locale` object.  This returns `None` if used outside of
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
    `pytz.timezone` object.  This returns `None` if used outside of
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


# def refresh():
#     """Refreshes the cached timezones and locale information.  This can
#     be used to switch a translation between a request and if you want
#     the changes to take place immediately, not just with the next request::
#
#         user.timezone = request.form['timezone']
#         user.locale = request.form['locale']
#         refresh()
#         flash(gettext('Language was changed'))
#
#     Without that refresh, the :func:`~flask.flash` function would probably
#     return English text and a now German page.
#     """
#     ctx = _request_ctx_stack.top
#     for key in 'babel_locale', 'babel_tzinfo', 'babel_translations':
#         if hasattr(ctx, key):
#             delattr(ctx, key)


def _get_formatter(key, format):
    """A small helper for the datetime formatting functions.  Looks up
    format defaults for different kinds.
    """
    locale = get_locale()
    icu = _request_ctx_stack.top.app.extensions['icu']
    if format is None:
        format = icu.date_formats[key]
    if format in ('short', 'medium', 'long', 'full'):
        tmp = icu.date_formats["{}.{}".format(key, format)]
        is_custom = False if tmp is None else True
        format = tmp if is_custom else icu.icu_date_formats[format]
    if is_custom:
        formatter = SimpleDateFormat(format, locale)
    else:
        if key is 'time':
            formatter = DateFormat.createTimeInstance(format, locale)
        if key is 'date':
            formatter = DateFormat.createDateInstance(format, locale)
        if key is 'datetime':
            formatter = DateFormat.createDateTimeInstance(format, format, locale)
    return formatter


# def to_user_timezone(datetime):
#     """Convert a datetime object to the user's timezone.  This automatically
#     happens on all date formatting unless rebasing is disabled.  If you need
#     to convert a :class:`datetime.datetime` object at any time to the user's
#     timezone (as returned by :func:`get_timezone` this function can be used).
#     """
#     if datetime.tzinfo is None:
#         datetime = datetime.replace(tzinfo=UTC)
#     tzinfo = get_timezone()
#     return tzinfo.normalize(datetime.astimezone(tzinfo))
#
#
# def to_utc(datetime):
#     """Convert a datetime object to UTC and drop tzinfo.  This is the
#     opposite operation to :func:`to_user_timezone`.
#     """
#     if datetime.tzinfo is None:
#         datetime = get_timezone().localize(datetime)
#     return datetime.astimezone(UTC).replace(tzinfo=None)
#
#
def format_datetime(datetime=None, format=None, rebase=True):
    """Return a date formatted according to the given pattern.  If no
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
    named `datetimeformat`.
    """
    formatter = _get_formatter('datetime', format)
    return _date_format(formatter, datetime, rebase)


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
    formatter = _get_formatter('date', format)
    return _date_format(formatter, date, rebase)


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
    formatter = _get_formatter('time', format)
    return _date_format(formatter, time, rebase)


# def format_timedelta(datetime_or_timedelta, granularity='second'):
#     """Format the elapsed time from the given date to now or the given
#     timedelta.  This currently requires an unreleased development
#     version of Babel.
#
#     This function is also available in the template context as filter
#     named `timedeltaformat`.
#     """
#     if isinstance(datetime_or_timedelta, datetime):
#         datetime_or_timedelta = datetime.utcnow() - datetime_or_timedelta
#     return dates.format_timedelta(datetime_or_timedelta, granularity,
#                                   locale=get_locale())
#
#
def _date_format(formatter, date, rebase):
    """Internal helper that formats the date."""
    if rebase:
        formatter.setTimeZone(get_timezone())
    return formatter.format(date)


# def format_number(number):
#     """Return the given number formatted for the locale in request
#
#     :param number: the number to format
#     :return: the formatted number
#     :rtype: unicode
#     """
#     locale = get_locale()
#     return numbers.format_number(number, locale=locale)
#
#
# def format_decimal(number, format=None):
#     """Return the given decimal number formatted for the locale in request
#
#     :param number: the number to format
#     :param format: the format to use
#     :return: the formatted number
#     :rtype: unicode
#     """
#     locale = get_locale()
#     return numbers.format_decimal(number, format=format, locale=locale)
#
#
# def format_currency(number, currency, format=None):
#     """Return the given number formatted for the locale in request
#
#     :param number: the number to format
#     :param currency: the currency code
#     :param format: the format to use
#     :return: the formatted number
#     :rtype: unicode
#     """
#     locale = get_locale()
#     return numbers.format_currency(
#         number, currency, format=format, locale=locale
#     )
#
#
# def format_percent(number, format=None):
#     """Return formatted percent value for the locale in request
#
#     :param number: the number to format
#     :param format: the format to use
#     :return: the formatted percent number
#     :rtype: unicode
#     """
#     locale = get_locale()
#     return numbers.format_percent(number, format=format, locale=locale)
#
#
# def format_scientific(number, format=None):
#     """Return value formatted in scientific notation for the locale in request
#
#     :param number: the number to format
#     :param format: the format to use
#     :return: the formatted percent number
#     :rtype: unicode
#     """
#     locale = get_locale()
#     return numbers.format_scientific(number, format=format, locale=locale)

def format(string, values=None):
    """Translates a string with the given current locale"""

    ctx = _request_ctx_stack.top
    locale = get_locale()
    icu_msg = get_message(string)
    msg = MessageFormat(icu_msg)
    if values is not None:
        args = list(values.keys())
        values = list(map(lambda v : Formattable(v), values.values()))
        return msg.format(args, values)
    return msg.format('')
