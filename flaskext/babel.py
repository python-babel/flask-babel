# -*- coding: utf-8 -*-
"""
    flaskext.babel
    ~~~~~~~~~~~~~~

    Implements i18n/l10n support for Flask applications based on Babel.

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import absolute_import
import os

# this is a workaround for a snow leopard bug that babel does not
# work around :)
if os.environ.get('LC_CTYPE', '').lower() == 'utf-8':
    os.environ['LC_CTYPE'] = 'en_US.utf-8'

from datetime import datetime
from flask import _request_ctx_stack
from babel import dates, support, Locale
from pytz import timezone, UTC
from werkzeug import ImmutableDict
from jinja2.environment import load_extensions


class Babel(object):
    """Central controller class that can be used to configure how
    babel behaves.
    """

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

    def __init__(self, app, default_locale='en', default_timezone='UTC',
                 date_formats=None, configure_jinja=True):
        self.app = app
        app.babel_instance = self

        self.app.config.setdefault('BABEL_DEFAULT_LOCALE', default_locale)
        self.app.config.setdefault('BABEL_DEFAULT_TIMEZONE', default_timezone)
        if date_formats is None:
            date_formats = self.default_date_formats.copy()
        self.date_formats = date_formats

        self.locale_selector_func = None
        self.timezone_selector_func = None

        if configure_jinja:
            app.jinja_env.filters.update(
                datetimeformat=format_datetime,
                dateformat=format_date,
                timeformat=format_time,
                timedeltaformat=format_timedelta
            )
            app.jinja_env.add_extension('jinja2.ext.i18n')
            app.jinja_env.install_gettext_callables(
                lambda x: get_translations().ugettext(x),
                lambda s, p, n: get_translations().ungettext(s, p, n),
                newstyle=True
            )

    def localeselector(self, f):
        self.locale_selector_func = f
        return f

    def timezoneselector(self, f):
        self.timezone_selector_func = f
        return f

    @property
    def default_locale(self):
        return Locale.parse(self.app.config['BABEL_DEFAULT_LOCALE'])

    @property
    def default_timezone(self):
        return timezone(self.app.config['BABEL_DEFAULT_TIMEZONE'])


def get_translations():
    """Returns the correct gettext translations"""
    ctx = _request_ctx_stack.top
    translations = getattr(ctx, 'babel_translations', None)
    if translations is None:
        dirname = os.path.join(ctx.app.root_path, 'translations')
        translations = support.Translations.load(dirname, [get_locale()])
        ctx.babel_translations = translations
    return translations


def get_locale():
    """Returns the locale that should be used."""
    ctx = _request_ctx_stack.top
    locale = getattr(ctx, 'babel_locale', None)
    if locale is None:
        babel = ctx.app.babel_instance
        if babel.locale_selector_func is None:
            locale = babel.default_locale
        else:
            rv = babel.locale_selector_func()
            if rv is None:
                locale = babel.default_locale
            else:
                locale = Locale.parse(rv)
        ctx.babel_locale = locale
    return locale


def get_timezone():
    """Returns the timezone that should be used."""
    ctx = _request_ctx_stack.top
    tzinfo = getattr(ctx, 'babel_tzinfo', None)
    if tzinfo is None:
        babel = ctx.app.babel_instance
        if babel.timezone_selector_func is None:
            tzinfo = babel.default_timezone
        else:
            rv = babel.timezone_selector_func()
            if rv is None:
                tzinfo = babel.default_timezone
            else:
                if isinstance(rv, basestring):
                    tzinfo = timezone(rv)
                else:
                    tzinfo = rv
        ctx.babel_tzinfo = tzinfo
    return tzinfo


def refresh():
    """Refreshes the cached timezones and locale information"""
    ctx = _request_ctx_stack.top
    for key in 'babel_locale', 'babel_tzinfo', 'babel_translations':
        if hasattr(ctx, key):
            delattr(ctx, key)


def _get_format(key, format):
    """A small helper for the datetime formatting functions.  Looks up
    format defaults for different kinds.
    """
    babel = _request_ctx_stack.top.app.babel_instance
    if format is None:
        format = babel.date_formats[key]
    if format in ('short', 'medium', 'full', 'long'):
        rv = babel.date_formats['%s.%s' % (key, format)]
        if rv is not None:
            format = rv
    return format


def to_user_timezone(datetime):
    """Convert a datetime object to the user's timezone."""
    if datetime.tzinfo is None:
        datetime = datetime.replace(tzinfo=UTC)
    tzinfo = get_timezone()
    return tzinfo.normalize(datetime.astimezone(tzinfo))


def to_utc(datetime):
    """Convert a datetime object to UTC and drop tzinfo."""
    if datetime.tzinfo is None:
        datetime = get_timezone().localize(datetime)
    return datetime.astimezone(UTC).replace(tzinfo=None)


def format_datetime(datetime=None, format=None, rebase=True):
    """Return a date formatted according to the given pattern."""
    format = _get_format('datetime', format)
    return _date_format(dates.format_datetime, datetime, format, rebase)


def format_date(date=None, format=None, rebase=True):
    """Return the date formatted according to the pattern.  Rebasing only
    works for datetime objects passed to this function obviously.
    """
    if rebase and isinstance(date, datetime):
        date = to_user_timezone(date)
    format = _get_format('date', format)
    return _date_format(dates.format_date, date, format, rebase)


def format_time(time=None, format=None, rebase=True):
    """Return the time formatted according to the pattern."""
    format = _get_format('time', format)
    return _date_format(dates.format_time, time, format, rebase)


def format_timedelta(datetime_or_timedelta, granularity='second'):
    """Format the elapsed time from the given date to now of the given
    timedelta.
    """
    if isinstance(datetime_or_timedelta, datetime):
        datetime_or_timedelta = datetime.utcnow() - datetime_or_timedelta
    return dates.format_timedelta(datetime_or_timedelta, granularity,
                                  locale=get_locale())


def _date_format(formatter, obj, format, rebase, **extra):
    """Internal helper that formats the date."""
    locale = get_locale()
    extra = {}
    if formatter is not dates.format_date and rebase:
        extra['tzinfo'] = get_timezone()
    return formatter(obj, format, locale=locale, **extra)


def gettext(string, **variables):
    return get_translations().ugettext(string) % variables
_ = gettext


def ngettext(singular, plural, num, **variables):
    variables.setdefault('num', num)
    return get_translations().ungettext(singular, plural, num) % variables
