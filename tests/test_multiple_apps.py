import flask
import flask_babel as babel


def test_multiple_apps():
    b = babel.Babel()

    app1 = flask.Flask(__name__)
    b.init_app(app1, default_locale='de_DE')

    app2 = flask.Flask(__name__)
    b.init_app(app2, default_locale='en_US')

    with app1.test_request_context():
        assert str(babel.get_locale()) == 'de_DE'
        assert babel.gettext(u'Hello %(name)s!', name='Peter') == \
               'Hallo Peter!'

    with app2.test_request_context():
        assert str(babel.get_locale()) == 'en_US'
        assert babel.gettext(u'Hello %(name)s!', name='Peter') == \
               'Hello Peter!'
