# -*- coding: utf-8 -*-
from __future__ import with_statement

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from decimal import Decimal
import flask
from datetime import datetime
from pytz import timezone
from flask_icu import *
from flask_icu._compat import text_type


class DateFormattingTestCase(unittest.TestCase):

    def test_basics(self):
        app = flask.Flask(__name__)
        icu = ICU(app)
        d = datetime(2010, 4, 12, 13, 46)
        d_utc = timezone('UTC').localize(d)

        with app.test_request_context():
            assert format_datetime(d_utc) == 'Apr 12, 2010, 1:46:00 PM'
            assert format_date(d_utc) == 'Apr 12, 2010'
            assert format_time(d_utc) == '1:46:00 PM'

        with app.test_request_context():
            app.config['ICU_DEFAULT_TIMEZONE'] = 'Europe/Berlin'
            assert format_datetime(d_utc) == 'Apr 12, 2010, 3:46:00 PM'
            assert format_date(d_utc) == 'Apr 12, 2010'
            assert format_time(d_utc) == '3:46:00 PM'

        with app.test_request_context():
            app.config['ICU_DEFAULT_LOCALE'] = 'it_IT'
            assert format_datetime(d_utc, 'long') == \
                '12 aprile 2010 15:46:00 CEST'

    def test_basics_with_none_for_defaults(self):
        app = flask.Flask(__name__)
        icu = ICU(app, None, None)
        d = datetime(2010, 4, 12, 13, 46)
        d_utc = timezone('UTC').localize(d)

        with app.test_request_context():
            assert format_datetime(d_utc) == 'Apr 12, 2010, 1:46:00 PM'

    def test_custom_formats(self):
        app = flask.Flask(__name__)
        app.config.update(
            ICU_DEFAULT_LOCALE='en_US',
            ICU_DEFAULT_TIMEZONE='Pacific/Johnston'
        )
        icu = ICU(app)
        icu.date_formats['datetime'] = 'long'
        icu.date_formats['datetime.long'] = 'MMMM d, yyyy h:mm:ss a'
        d = datetime(2010, 4, 12, 13, 46)
        d_utc= timezone('UTC').localize(d)

        with app.test_request_context():
            assert format_datetime(d_utc) == 'April 12, 2010 3:46:00 AM'

    # def test_custom_locale_selector(self):
    #     app = flask.Flask(__name__)
    #     icu = ICU(app)
    #     d = datetime(2010, 4, 12, 13, 46)
    #     d_utc = timezone('UTC').localize(d)
    #
    #     the_timezone = 'UTC'
    #     the_locale = 'en_US'
    #
    #     @icu.localeselector
    #     def select_locale():
    #         return the_locale
    #     @icu.timezoneselector
    #     def select_timezone():
    #         return the_timezone
    #
    #     with app.test_request_context():
    #         assert format_datetime(d_utc) == 'Apr 12, 2010, 1:46:00 PM'
    #
    #     the_locale = 'it_IT'
    #     the_timezone = 'Europe/Vienna'
    #
    #     with app.test_request_context():
    #         assert format_datetime(d_utc) == '12 apr 2010, 15:46:00'

    def test_refreshing(self):
        app = flask.Flask(__name__)
        icu = ICU(app)
        d = datetime(2010, 4, 12, 13, 46)
        d_utc = timezone('UTC').localize(d)

        with app.test_request_context():
            assert format_datetime(d_utc) == 'Apr 12, 2010, 1:46:00 PM'
            app.config['ICU_DEFAULT_TIMEZONE'] = 'Europe/Vienna'
            icu_refresh()
            assert format_datetime(d_utc) == 'Apr 12, 2010, 3:46:00 PM'


class NumberFormattingTestCase(unittest.TestCase):

    def test_basics(self):
        app = flask.Flask(__name__)
        icu = ICU(app)
        n = 1099

        app.config['ICU_DEFAULT_LOCALE'] = 'en_US'
        with app.test_request_context():
            assert format_number(n) == u'1,099'
            assert format_decimal(Decimal('1010.99')) == u'1,010.99'
            assert format_currency(n) == '$1,099.00'
            assert format_currency(n, 'ILS') == '₪1,099.00'
            assert format_percent(0.19) == '19%'
            assert format_scientific(10000) == u'1E4'

        app.config['ICU_DEFAULT_LOCALE'] = 'de_DE'
        with app.test_request_context():
            # Make sure it actually formats based on locale
            assert format_number(n) == u'1.099'
            assert format_decimal(Decimal('1010.99')) == u'1.010,99'
            assert format_currency(n) == '1.099,00€'
            assert format_currency(n, 'USD') == '1.099,00$'
            assert format_currency(n, 'ILS') == '1.099,00₪'
            assert format_percent(0.19) == '19%'
            assert format_scientific(10000) == u'1E4'

class MessageFormattingTestCases(unittest.TestCase):

    def test_simple_message(self):
        app = flask.Flask(__name__)
        icu = ICU(app, default_locale='en')

        with app.test_request_context():
            assert format('Hello {name}!', {'name': 'Peter'}) == 'Hello Peter!'
            # Test that values dict ordering is safe.
            values = {'a': 'Bob', 'z': 'Sally', '0': 'Nobody', '2x': 'Ruby'}
            values['z'] = "John"
            values['new'] = "Who?"
            assert format('{z} and {a} and {2x} and {new} and {0} like this library.', values) \
                == 'John and Bob and Ruby and Who? and Nobody like this library.'


        with app.test_request_context():
            app.config['ICU_DEFAULT_LOCALE'] = 'de'
            icu_refresh()
            assert format('Hello {name}!', {'name': 'Peter'}) == 'Hallo Peter!'

    def test_non_existant_message(self):
        app = flask.Flask(__name__)
        icu = ICU(app, default_locale='en')

        with app.test_request_context():
            assert format('This message does not exist') == 'This message does not exist'


    def test_icu_plural(self):
        app = flask.Flask(__name__)
        icu = ICU(app, default_locale='en')

        with app.test_request_context():
            assert format("I have {numApples, plural, \
                =0 {no apples} \
                one {one apple} \
                other {# apples}}.", {'numApples': 0}) == 'I have no apples.'
            assert format("I have {numApples, plural, \
                =0 {no apples} \
                one {one apple} \
                other {# apples}}.", {'numApples': 1}) == 'I have one apple.'
            assert format("I have {numApples, plural, \
                =0 {no apples} \
                one {one apple} \
                other {# apples}}.", {'numApples': 3}) == 'I have 3 apples.'


        with app.test_request_context():
            app.config['ICU_DEFAULT_LOCALE'] = 'de'
            icu_refresh()
            assert format("Hello {name}!", {'name': 'Peter'}) == "Hallo Peter!"
            assert format("I have {numApples, plural, \
                =0 {no apples} \
                one {one apple} \
                other {# apples}}.", {'numApples': 0}) == 'Ich habe keine Äpfeln.'
            assert format("I have {numApples, plural, \
                =0 {no apples} \
                one {one apple} \
                other {# apples}}.", {'numApples': 1}) == 'Ich habe einen Apfel.'
            assert format("I have {numApples, plural, \
                =0 {no apples} \
                one {one apple} \
                other {# apples}}.", {'numApples': 3}) == 'Ich habe 3 Äpfeln.'

    def test_icu_select(self):
        app = flask.Flask(__name__)
        icu = ICU(app, default_locale='en')

        with app.test_request_context():
            assert 'He will respond shortly.' == \
                format("{gender, select, \
                    male {He} \
                    female {She} \
                    other {They}} will respond shortly.", {'gender': 'male'})
            assert 'She will respond shortly.' == \
                format("{gender, select, \
                    male {He} \
                    female {She} \
                    other {They}} will respond shortly.", {'gender': 'female'})

        with app.test_request_context():
            app.config['ICU_DEFAULT_LOCALE'] = 'de'
            icu_refresh()
            assert 'Er wird antworten in Kürze.' == \
                format("{gender, select, \
                    male {He} \
                    female {She} \
                    other {They}} will respond shortly.", {'gender': 'male'})
            assert 'Sie wird antworten in Kürze.' == \
                format("{gender, select, \
                    male {He} \
                    female {She} \
                    other {They}} will respond shortly.", {'gender': 'female'})


    def test_list_translations(self):
        app = flask.Flask(__name__)
        icu = ICU(app, default_locale='de')
        translations = icu.list_translations()
        assert len(translations) == 2
        assert ('en' in translations and 'de' in translations)


if __name__ == '__main__':
    unittest.main()
