import flask
import pytest
from babel import Locale, UnknownLocaleError

import flask_babel as babel


@pytest.mark.parametrize(
    "selected, expected",
    [
        ("pt-BR", "pt_BR"),
        ("zh-Hant-TW", "zh_Hant_TW"),
        ("pt_BR", "pt_BR"),
        ("en_US.UTF-8", "en_US"),
        ("de_DE@custom-modifier", "de_DE@custom-modifier"),
        ("en", "en"),
        (Locale("pt", territory="BR"), "pt_BR"),
        (None, "de_DE"),
    ],
)
def test_locale_selector(selected, expected):
    app = flask.Flask(__name__)
    calls = []

    def select_locale():
        calls.append(True)
        return selected

    babel.Babel(app, default_locale="de_DE", locale_selector=select_locale)
    with app.test_request_context():
        locale = babel.get_locale()
        assert str(locale) == expected
        assert babel.get_locale() is locale
        assert len(calls) == 1
        babel.refresh()
        assert str(babel.get_locale()) == expected
        assert len(calls) == 2


@pytest.mark.parametrize(
    "selected, error",
    [("pt--BR", ValueError), ("zz-ZZ", UnknownLocaleError)],
)
def test_invalid_locale_selector(selected, error):
    app = flask.Flask(__name__)
    babel.Babel(app, locale_selector=lambda: selected)
    with app.test_request_context(), pytest.raises(error):
        babel.get_locale()
