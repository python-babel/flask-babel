import flask
import pytest

import flask_babel as babel


@pytest.mark.parametrize(
    "timestamp, utc_date, los_angeles_date",
    [
        (0, "1970-01-01", "1969-12-31"),
        (-1, "1969-12-31", "1969-12-31"),
        (1704069000, "2024-01-01", "2023-12-31"),
        (1704069000.5, "2024-01-01", "2023-12-31"),
    ],
)
@pytest.mark.parametrize("rebase", [True, False])
def test_timestamp_date_formatting(timestamp, utc_date, los_angeles_date, rebase):
    app = flask.Flask(__name__)
    babel.Babel(app, default_timezone="America/Los_Angeles")
    expected = los_angeles_date if rebase else utc_date
    with app.test_request_context():
        assert babel.format_date(timestamp, "yyyy-MM-dd", rebase=rebase) == expected
        assert (
            flask.render_template_string(
                '{{ value|dateformat("yyyy-MM-dd", rebase=rebase) }}',
                value=timestamp,
                rebase=rebase,
            )
            == expected
        )


def test_timestamp_date_in_positive_timezone():
    app = flask.Flask(__name__)
    babel.Babel(app, default_timezone="Asia/Tokyo")
    with app.test_request_context():
        assert babel.format_date(-1, "yyyy-MM-dd") == "1970-01-01"
