import pickle

import flask
from babel.support import NullTranslations

import flask_babel as babel
from flask_babel import get_translations, gettext, lazy_gettext


def test_no_request_context():
    b = babel.Babel()
    app = flask.Flask(__name__)
    b.init_app(app)

    with app.app_context():
        assert isinstance(get_translations(), NullTranslations)


def test_multiple_directories():
    """
    Ensure we can load translations from multiple directories.

    This also ensures that directories without any translation files
    are not taken into account.
    """
    b = babel.Babel()
    app = flask.Flask(__name__)

    app.config.update(
        {
            "BABEL_TRANSLATION_DIRECTORIES": ";".join(
                ("translations", "renamed_translations")
            ),
            "BABEL_DEFAULT_LOCALE": "de_DE",
        }
    )

    b.init_app(app)

    with app.test_request_context():
        translations = b.list_translations()

        assert len(translations) == 4
        assert str(translations[0]) == "de"
        assert str(translations[1]) == "ja"
        assert str(translations[2]) == "de"
        assert str(translations[3]) == "de_DE"

        assert gettext("Hello %(name)s!", name="Peter") == "Hallo Peter!"


def test_multiple_directories_multiple_domains():
    """
    Ensure we can load translations from multiple directories with a
    custom domain.
    """
    b = babel.Babel()
    app = flask.Flask(__name__)

    app.config.update(
        {
            "BABEL_TRANSLATION_DIRECTORIES": ";".join(
                (
                    "renamed_translations",
                    "translations_different_domain",
                )
            ),
            "BABEL_DEFAULT_LOCALE": "de_DE",
            "BABEL_DOMAIN": ";".join(
                (
                    "messages",
                    "myapp",
                )
            ),
        }
    )

    b.init_app(app)

    with app.test_request_context():
        translations = b.list_translations()

        assert len(translations) == 3
        assert str(translations[0]) == "de"
        assert str(translations[1]) == "de"
        assert str(translations[2]) == "de_DE"

        assert gettext("Hello %(name)s!", name="Peter") == "Hallo Peter!"
        assert gettext("Good bye") == "Auf Wiedersehen"


def test_multiple_directories_different_domain():
    """
    Ensure we can load translations from multiple directories with a
    custom domain.
    """
    b = babel.Babel()
    app = flask.Flask(__name__)

    app.config.update(
        {
            "BABEL_TRANSLATION_DIRECTORIES": ";".join(
                ("translations_different_domain", "renamed_translations")
            ),
            "BABEL_DEFAULT_LOCALE": "de_DE",
            "BABEL_DOMAIN": "myapp",
        }
    )

    b.init_app(app)

    with app.test_request_context():
        translations = b.list_translations()

        assert len(translations) == 3
        assert str(translations[0]) == "de"
        assert str(translations[1]) == "de"
        assert str(translations[2]) == "de_DE"

        assert gettext("Hello %(name)s!", name="Peter") == "Hallo Peter!"
        assert gettext("Good bye") == "Auf Wiedersehen"


def test_different_domain():
    """
    Ensure we can load translations from multiple directories.
    """
    b = babel.Babel()
    app = flask.Flask(__name__)

    app.config.update(
        {
            "BABEL_TRANSLATION_DIRECTORIES": "translations_different_domain",
            "BABEL_DEFAULT_LOCALE": "de_DE",
            "BABEL_DOMAIN": "myapp",
        }
    )

    b.init_app(app)

    with app.test_request_context():
        translations = b.list_translations()

        assert len(translations) == 2
        assert str(translations[0]) == "de"
        assert str(translations[1]) == "de_DE"

        assert gettext("Good bye") == "Auf Wiedersehen"


def test_lazy_old_style_formatting():
    lazy_string = lazy_gettext("Hello %(name)s")
    assert lazy_string % {"name": "test"} == "Hello test"

    lazy_string = lazy_gettext("test")
    assert "Hello %s" % lazy_string == "Hello test"


def test_lazy_pickling():
    lazy_string = lazy_gettext("Foo")
    pickled = pickle.dumps(lazy_string)
    unpickled = pickle.loads(pickled)

    assert unpickled == lazy_string
