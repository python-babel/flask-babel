from datetime import datetime, timedelta

import flask

import flask_babel as babel
from flask_babel import get_babel


def test_basics():
    app = flask.Flask(__name__)
    babel.Babel(app)
    d = datetime(2010, 4, 12, 13, 46)
    delta = timedelta(days=6)

    with app.test_request_context():
        assert babel.format_datetime(d) == 'Apr 12, 2010, 1:46:00 PM'
        assert babel.format_date(d) == 'Apr 12, 2010'
        assert babel.format_time(d) == '1:46:00 PM'
        assert babel.format_timedelta(delta) == '1 week'
        assert babel.format_timedelta(delta, threshold=1) == '6 days'

    with app.test_request_context():
        get_babel(app).default_timezone = 'Europe/Vienna'
        assert babel.format_datetime(d) == 'Apr 12, 2010, 3:46:00 PM'
        assert babel.format_date(d) == 'Apr 12, 2010'
        assert babel.format_time(d) == '3:46:00 PM'

    with app.test_request_context():
        get_babel(app).default_locale = 'de_DE'
        assert babel.format_datetime(d, 'long') == \
            '12. April 2010 um 15:46:00 MESZ'


def test_custom_formats():
    app = flask.Flask(__name__)
    app.config.update(
        BABEL_DEFAULT_LOCALE='en_US',
        BABEL_DEFAULT_TIMEZONE='Pacific/Johnston'
    )
    b = babel.Babel(app)
    b.date_formats['datetime'] = 'long'
    b.date_formats['datetime.long'] = 'MMMM d, yyyy h:mm:ss a'
    d = datetime(2010, 4, 12, 13, 46)

    with app.test_request_context():
        assert babel.format_datetime(d) == 'April 12, 2010 3:46:00 AM'


def test_custom_locale_selector():
    app = flask.Flask(__name__)
    b = babel.Babel(app)
    d = datetime(2010, 4, 12, 13, 46)

    the_timezone = 'UTC'
    the_locale = 'en_US'

    def select_locale():
        return the_locale

    def select_timezone():
        return the_timezone

    get_babel(app).locale_selector = select_locale
    get_babel(app).timezone_selector = select_timezone

    with app.test_request_context():
        assert babel.format_datetime(d) == 'Apr 12, 2010, 1:46:00 PM'

    the_locale = 'de_DE'
    the_timezone = 'Europe/Vienna'

    with app.test_request_context():
        assert babel.format_datetime(d) == '12.04.2010, 15:46:00'


def test_refreshing():
    app = flask.Flask(__name__)
    babel.Babel(app)
    d = datetime(2010, 4, 12, 13, 46)
    with app.test_request_context():
        assert babel.format_datetime(d) == 'Apr 12, 2010, 1:46:00 PM'
        get_babel(app).default_timezone = 'Europe/Vienna'
        babel.refresh()
        assert babel.format_datetime(d) == 'Apr 12, 2010, 3:46:00 PM'
