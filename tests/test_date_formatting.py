import pytz
from datetime import datetime, timedelta, timezone

import flask

import flask_babel as babel
from flask_babel import get_babel
import time_machine


def test_basics():
    london = pytz.timezone("Europe/London")
    app = flask.Flask(__name__)
    babel.Babel(app)
    d = datetime(2010, 4, 12, 13, 46)
    d_tzinfo_non_dst = london.localize(datetime(2010, 1, 16, 23, 23)) # non-DST
    d_tzinfo_dst = london.localize(datetime(2010, 8, 12, 5, 13)) # DST
    delta = timedelta(days=6)

    with app.test_request_context():
        assert babel.format_datetime(d) == 'Apr 12, 2010, 1:46:00\u202fPM'
        assert babel.format_datetime(d_tzinfo_non_dst) == \
            "Jan 16, 2010, 11:23:00\u202fPM"
        assert babel.format_datetime(d_tzinfo_dst) == \
            "Aug 12, 2010, 4:13:00\u202fAM"
        assert babel.format_date(d) == 'Apr 12, 2010'
        assert babel.format_time(d) == '1:46:00\u202fPM'
        assert babel.format_timedelta(delta) == '1 week'
        assert babel.format_timedelta(delta, threshold=1) == '6 days'

        with time_machine.travel(datetime(2010, 4, 12, 14, tzinfo=timezone.utc)):
            assert babel.format_timedelta(d) == "14 minutes"
        with time_machine.travel(datetime(2010, 1, 16, 23, 30, tzinfo=timezone.utc)):
            assert babel.format_timedelta(d_tzinfo_non_dst) == "7 minutes"
        with time_machine.travel(datetime(2010, 8, 12, 4, 30, tzinfo=timezone.utc)):
            assert babel.format_timedelta(d_tzinfo_dst) == "17 minutes"

    with app.test_request_context():
        get_babel(app).default_timezone = 'Europe/Vienna'
        assert babel.format_datetime(d) == 'Apr 12, 2010, 3:46:00\u202fPM'
        assert babel.format_datetime(d_tzinfo_non_dst) == \
            "Jan 17, 2010, 12:23:00\u202fAM"
        assert babel.format_datetime(d_tzinfo_dst) == \
            "Aug 12, 2010, 6:13:00\u202fAM"
        assert babel.format_date(d) == 'Apr 12, 2010'
        assert babel.format_time(d) == '3:46:00\u202fPM'

        with time_machine.travel(datetime(2010, 4, 12, 14, tzinfo=timezone.utc)):
            assert babel.format_timedelta(d) == "14 minutes"
        with time_machine.travel(datetime(2010, 1, 16, 23, 30, tzinfo=timezone.utc)):
            assert babel.format_timedelta(d_tzinfo_non_dst) == "7 minutes"
        with time_machine.travel(datetime(2010, 8, 12, 4, 30, tzinfo=timezone.utc)):
            assert babel.format_timedelta(d_tzinfo_dst) == "17 minutes"

    with app.test_request_context():
        get_babel(app).default_locale = 'de_DE'
        assert babel.format_datetime(d, 'long') == \
            '12. April 2010, 15:46:00 MESZ'


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
        assert babel.format_datetime(d) == 'Apr 12, 2010, 1:46:00\u202fPM'

    the_locale = 'de_DE'
    the_timezone = 'Europe/Vienna'

    with app.test_request_context():
        assert babel.format_datetime(d) == '12.04.2010, 15:46:00'


def test_refreshing():
    app = flask.Flask(__name__)
    babel.Babel(app)
    d = datetime(2010, 4, 12, 13, 46)
    with app.test_request_context():
        assert babel.format_datetime(d) == 'Apr 12, 2010, 1:46:00\u202fPM'
        get_babel(app).default_timezone = 'Europe/Vienna'
        babel.refresh()
        assert babel.format_datetime(d) == 'Apr 12, 2010, 3:46:00\u202fPM'
