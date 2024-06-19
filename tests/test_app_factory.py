import flask
import flask_babel as babel


def test_app_factory():
    b = babel.Babel()

    def locale_selector():
        return 'de_DE'

    def create_app():
        app_ = flask.Flask(__name__)
        b.init_app(
            app_,
            default_locale='en_US',
            locale_selector=locale_selector
        )
        return app_

    app = create_app()
    with app.test_request_context():
        assert str(babel.get_locale()) == 'de_DE'
        assert babel.gettext(u'Hello %(name)s!', name='Peter') == \
               'Hallo Peter!'
