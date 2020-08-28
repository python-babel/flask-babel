import os

from contextlib import contextmanager
from flask import current_app, request
from flask.ctx import has_request_context
from flask.helpers import locked_cached_property
from babel import support, Locale
from pytz import timezone

from flask_babel.speaklater import LazyString


class Babel(object):
    def __init__(self, app=None, default_locale='en', default_timezone='UTC',
                 default_domain='messages', configure_jinja=True):
        self._default_locale = default_locale
        self._default_timezone = default_timezone
        self._default_domain = default_domain
        self._configure_jinja = configure_jinja

        self.app = app
        self.locale_selector_func = None
        self.timezone_selector_func = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Set up this instance for use with *app*, if no app was passed to
        the constructor.
        """
        self.app = app

        if not hasattr(app, 'extensions'):
            app.extensions = {}

        # Several extensions, such as Flask-WTF, check for this value before
        # using get_locale. Don't remove or rename without thought.
        app.extensions['babel'] = self

        self._default_locale = Locale.parse(
            app.config.get('BABEL_DEFAULT_LOCALE', self._default_locale)
        )
        self._default_timezone = timezone(
            app.config.get('BABEL_DEFAULT_TIMEZONE', self._default_timezone)
        )

        self._default_domain = app.config.get(
            'BABEL_DEFAULT_DOMAIN',
            app.config.get(
                # Legacy configuration key.
                'BABEL_DOMAIN',
                self._default_timezone
            )
        )

        if self._configure_jinja:
            app.jinja_env.add_extension('jinja2.ext.i18n')
            app.jinja_env.install_gettext_callables(
                lambda x: get_translations().ugettext(x),
                lambda s, p, n: get_translations().ungettext(s, p, n),
                newstyle=True
            )

    def localeselector(self, f):
        """Registers a callback function for locale selection.  The default
        behaves as if a function was registered that returns `None` all the
        time.  If `None` is returned, the locale falls back to the one from
        the configuration.

        This has to return the locale as string (eg: ``'de_AT'``, ``'en_US'``)
        """
        self.locale_selector_func = f
        return f

    def timezoneselector(self, f):
        """Registers a callback function for timezone selection.  The default
        behaves as if a function was registered that returns `None` all the
        time.  If `None` is returned, the timezone falls back to the one from
        the configuration.

        This has to return the timezone as string (eg: ``'Europe/Vienna'``)
        """
        self.timezone_selector_func = f
        return f

    def list_translations(self):
        """Returns a list of all the locales translations exist for.  The
        list returned will be filled with actual locale objects and not just
        strings.

        .. versionadded:: 0.6
        """
        result = []

        for dirname in self.translation_directories:
            if not os.path.isdir(dirname):
                continue

            for folder in os.listdir(dirname):
                locale_dir = os.path.join(dirname, folder, 'LC_MESSAGES')
                if not os.path.isdir(locale_dir):
                    continue

                if filter(lambda x: x.endswith('.mo'), os.listdir(locale_dir)):
                    result.append(Locale.parse(folder))

        # If not other translations are found, add the default locale.
        if not result:
            result.append(Locale.parse(self._default_locale))

        return result

    @property
    def default_locale(self) -> Locale:
        """The default locale from the configuration as instance of a
        `babel.Locale` object.
        """
        return self._default_locale

    @property
    def default_timezone(self) -> timezone:
        """The default timezone from the configuration as instance of a
        `pytz.timezone` object.
        """
        return self._default_timezone

    @property
    def domain(self):
        """The message domain for the translations as a string.
        """
        return self._default_domain

    @locked_cached_property
    def domain_instance(self) -> 'Domain':
        """The message domain for the translations.
        """
        return Domain(domain=self.app.config['BABEL_DOMAIN'])

    @property
    def translation_directories(self):
        directories = self.app.config.get(
            'BABEL_TRANSLATION_DIRECTORIES',
            'translations'
        ).split(';')

        for path in directories:
            if os.path.isabs(path):
                yield path
            else:
                yield os.path.join(self.app.root_path, path)


def get_translations():
    """Returns the correct gettext translations that should be used for
    this request.  This will never fail and return a dummy translation
    object if used outside of the request or if a translation cannot be
    found.
    """
    return get_domain().get_translations()


def get_locale():
    """Returns the locale that should be used for this request as
    `babel.Locale` object.  This returns `None` if used outside of
    a request.
    """
    ctx = _get_current_context()
    if ctx is None:
        return None

    locale = getattr(ctx, 'babel_locale', None)
    if locale is None:
        babel = current_app.extensions['babel']
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
    """Returns the timezone that should be used for this request as
    `pytz.timezone` object.  This returns `None` if used outside of
    a request.
    """
    ctx = _get_current_context()
    tzinfo = getattr(ctx, 'babel_tzinfo', None)
    if tzinfo is None:
        babel = current_app.extensions['babel']
        if babel.timezone_selector_func is None:
            tzinfo = babel.default_timezone
        else:
            rv = babel.timezone_selector_func()
            if rv is None:
                tzinfo = babel.default_timezone
            else:
                tzinfo = timezone(rv) if isinstance(rv, str) else rv
        ctx.babel_tzinfo = tzinfo
    return tzinfo


def refresh():
    """Refreshes the cached timezones and locale information.  This can
    be used to switch a translation between a request and if you want
    the changes to take place immediately, not just with the next request::

        user.timezone = request.form['timezone']
        user.locale = request.form['locale']
        refresh()
        flash(gettext('Language was changed'))

    Without that refresh, the :func:`~flask.flash` function would probably
    return English text and a now German page.
    """
    ctx = _get_current_context()
    for key in 'babel_locale', 'babel_tzinfo', 'babel_translations':
        if hasattr(ctx, key):
            delattr(ctx, key)

    if hasattr(ctx, 'forced_babel_locale'):
        ctx.babel_locale = ctx.forced_babel_locale


@contextmanager
def force_locale(locale):
    """Temporarily overrides the currently selected locale.

    Sometimes it is useful to switch the current locale to different one, do
    some tasks and then revert back to the original one. For example, if the
    user uses German on the web site, but you want to send them an email in
    English, you can use this function as a context manager::

        with force_locale('en_US'):
            send_email(gettext('Hello!'), ...)

    :param locale: The locale to temporary switch to (ex: 'en_US').
    """
    ctx = _get_current_context()
    if ctx is None:
        yield
        return

    orig_attrs = {}
    for key in ('babel_translations', 'babel_locale'):
        orig_attrs[key] = getattr(ctx, key, None)

    try:
        ctx.babel_locale = Locale.parse(locale)
        ctx.forced_babel_locale = ctx.babel_locale
        ctx.babel_translations = None
        yield
    finally:
        if hasattr(ctx, 'forced_babel_locale'):
            del ctx.forced_babel_locale

        for key, value in orig_attrs.items():
            setattr(ctx, key, value)


class Domain(object):
    """Localization domain.

    By default will look for translations in Flask application directory and
    "messages" domain.
    """
    def __init__(self, translation_directories=None, domain='messages'):
        if isinstance(translation_directories, str):
            translation_directories = [translation_directories]
        self._translation_directories = translation_directories
        self.domain = domain
        self.cache = {}

    def __repr__(self):
        return '<Domain({!r}, {!r})>'.format(
            self._translation_directories,
            self.domain
        )

    @property
    def translation_directories(self):
        if self._translation_directories is not None:
            return self._translation_directories
        babel = current_app.extensions['babel']
        return babel.translation_directories

    def as_default(self):
        """Set this domain as default for the current request"""
        ctx = _get_current_context()

        if ctx is None:
            raise RuntimeError("No request context")

        ctx.babel_domain = self

    def get_translations(self):
        ctx = _get_current_context()

        if ctx is None:
            return support.NullTranslations()

        locale = get_locale()
        try:
            return self.cache[str(locale), self.domain]
        except KeyError:
            translations = support.Translations()

            for dirname in self.translation_directories:
                catalog = support.Translations.load(
                    dirname,
                    [locale],
                    self.domain
                )
                translations.merge(catalog)
                # FIXME: Workaround for merge() being really, really stupid. It
                # does not copy _info, plural(), or any other instance
                # variables populated by GNUTranslations. We probably want to
                # stop using `support.Translations.merge` entirely.
                if hasattr(catalog, 'plural'):
                    translations.plural = catalog.plural

            self.cache[str(locale), self.domain] = translations
            return translations


def _get_current_context():
    if has_request_context():
        return request

    if current_app:
        return current_app


def get_domain():
    ctx = _get_current_context()
    if ctx is None:
        # this will use NullTranslations
        return Domain()

    try:
        return ctx.babel_domain
    except AttributeError:
        pass

    babel = current_app.extensions['babel']
    ctx.babel_domain = babel.domain_instance
    return ctx.babel_domain


def gettext(*args, **kwargs):
    return get_domain().gettext(*args, **kwargs)


_ = gettext


def ngettext(*args, **kwargs):
    return get_domain().ngettext(*args, **kwargs)


def pgettext(*args, **kwargs):
    return get_domain().pgettext(*args, **kwargs)


def npgettext(*args, **kwargs):
    return get_domain().npgettext(*args, **kwargs)


def lazy_gettext(*args, **kwargs):
    return LazyString(gettext, *args, **kwargs)


def lazy_pgettext(*args, **kwargs):
    return LazyString(pgettext, *args, **kwargs)


def lazy_ngettext(*args, **kwargs):
    return LazyString(ngettext, *args, **kwargs)
