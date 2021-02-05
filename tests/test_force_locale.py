from threading import Semaphore, Thread

import flask

import flask_babel as babel


def test_force_locale():
    app = flask.Flask(__name__)
    b = babel.Babel(app)

    @b.localeselector
    def select_locale():
        return 'de_DE'

    with app.test_request_context():
        assert str(babel.get_locale()) == 'de_DE'
        with babel.force_locale('en_US'):
            assert str(babel.get_locale()) == 'en_US'
        assert str(babel.get_locale()) == 'de_DE'


def test_force_locale_with_threading():
    app = flask.Flask(__name__)
    b = babel.Babel(app)

    @b.localeselector
    def select_locale():
        return 'de_DE'

    semaphore = Semaphore(value=0)

    def first_request():
        with app.test_request_context():
            with babel.force_locale('en_US'):
                assert str(babel.get_locale()) == 'en_US'
                semaphore.acquire()

    thread = Thread(target=first_request)
    thread.start()

    try:
        with app.test_request_context():
            assert str(babel.get_locale()) == 'de_DE'
    finally:
        semaphore.release()
        thread.join()


def test_refresh_during_force_locale():
    app = flask.Flask(__name__)
    b = babel.Babel(app)

    @b.localeselector
    def select_locale():
        return 'de_DE'

    with app.test_request_context():
        with babel.force_locale('en_US'):
            assert str(babel.get_locale()) == 'en_US'
            babel.refresh()
            assert str(babel.get_locale()) == 'en_US'
