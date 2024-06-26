from decimal import Decimal

import flask

import flask_babel as babel


def test_basics():
    app = flask.Flask(__name__)
    babel.Babel(app)
    n = 1099

    with app.test_request_context():
        assert babel.format_number(n) == "1,099"
        assert babel.format_decimal(Decimal("1010.99")) == "1,010.99"
        assert babel.format_currency(n, "USD") == "$1,099.00"
        assert babel.format_percent(0.19) == "19%"
        assert babel.format_scientific(10000) == "1E4"
