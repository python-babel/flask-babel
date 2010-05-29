from __future__ import with_statement
import unittest
import flask
from datetime import datetime
from flaskext import babel


class DateFormattingTestCase(unittest.TestCase):

    def test_basics(self):
        app = flask.Flask(__name__)
        b = babel.Babel(app)
        d = datetime(2010, 4, 12, 13, 46)

        with app.test_request_context():
            assert babel.format_datetime(d) == 'Apr 12, 2010 1:46:00 PM'
            assert babel.format_date(d) == 'Apr 12, 2010'
            assert babel.format_time(d) == '1:46:00 PM'

        with app.test_request_context():
            app.config['BABEL_DEFAULT_TIMEZONE'] = 'Europe/Vienna'
            assert babel.format_datetime(d) == 'Apr 12, 2010 3:46:00 PM'
            assert babel.format_date(d) == 'Apr 12, 2010'
            assert babel.format_time(d) == '3:46:00 PM'

        with app.test_request_context():
            app.config['BABEL_DEFAULT_LOCALE'] = 'de_DE'
            assert babel.format_datetime(d, 'long') == \
                '12. April 2010 15:46:00 MESZ'

    def test_custom_formats(self):
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

    def test_custom_locale_selector(self):
        app = flask.Flask(__name__)
        b = babel.Babel(app)
        d = datetime(2010, 4, 12, 13, 46)

        the_timezone = 'UTC'
        the_locale = 'en_US'

        @b.localeselector
        def select_locale():
            return the_locale
        @b.timezoneselector
        def select_timezone():
            return the_timezone

        with app.test_request_context():
            assert babel.format_datetime(d) == 'Apr 12, 2010 1:46:00 PM'

        the_locale = 'de_DE'
        the_timezone = 'Europe/Vienna'

        with app.test_request_context():
            assert babel.format_datetime(d) == '12.04.2010 15:46:00'

    def test_refreshing(self):
        app = flask.Flask(__name__)
        b = babel.Babel(app)
        d = datetime(2010, 4, 12, 13, 46)
        with app.test_request_context():
            assert babel.format_datetime(d) == 'Apr 12, 2010 1:46:00 PM'
            app.config['BABEL_DEFAULT_TIMEZONE'] = 'Europe/Vienna'
            babel.refresh()
            assert babel.format_datetime(d) == 'Apr 12, 2010 3:46:00 PM'


if __name__ == '__main__':
    unittest.main()
